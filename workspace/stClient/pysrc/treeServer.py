# -*- coding: utf-8 -*-

import sys
import os
import cPickle as pickle
import sysv_ipc
import ast
import json

import time
from tree import *
from configure import *

try:
    if sys.frozen:
        sys.setdefaultencoding("utf-8")
except:
    pass

SP = "|0s283hs1|" # data sparator

try:
    command_mq = sysv_ipc.MessageQueue(command_q_id, sysv_ipc.IPC_CREAT, max_message_size=MAX_MSG_SIZE)
    result_mq = sysv_ipc.MessageQueue(result_q_id, sysv_ipc.IPC_CREAT, max_message_size=MAX_MSG_SIZE)
except:
    command_mq = sysv_ipc.MessageQueue(command_q_id)
    result_mq = sysv_ipc.MessageQueue(result_q_id)


def treeServer_getTree(tree):
    if tree is not None:
        node_list = tree.getTreeNodeList()

        for i, node in enumerate(node_list):
            name = node.name
            path = node.path
            type = node.type
            mtime = node.mtime
            size = node.size

            offset_list = [cb.offset for cb in  node.new_compare_block_list]
            sha_hash_list = [cb.sha_hash for cb in node.new_compare_block_list]
            type_list = [cb.type for cb in node.new_compare_block_list]

            data = name + SP + path + SP + type + SP + str(mtime) + SP + str(size) + SP + str(offset_list) + SP + str(sha_hash_list) + SP + str(type_list)
            data = data.encode('utf-8')
            data_size = len(data)

            send_amount = int(round( (data_size / float(MAX_MSG_SIZE) + 0.5)))
            result_mq.send("GET_TREE_NODE_START" + SP + str(send_amount))

            for i in range(send_amount):
                if i == send_amount-1 :
                    send_data = data[MAX_MSG_SIZE * i :]
                else:
                    send_data = data[MAX_MSG_SIZE * i : MAX_MSG_SIZE * (i + 1)]

                result_mq.send(send_data)

            result_mq.send("GET_TREE_NODE_END"+ SP)

        result_mq.send("GET_TREE_END"+ SP)

        #Tree is None
    else:
        result_mq.send("GET_TREE_NONE" )

def treeServer_setTree(tree):
    while(True):
        command = command_mq.receive()[0]
        command_list = command.split(SP)

        if command_list[0] == "SET_TREE_END":
            result_mq.send("SET_TREE_OK")
            break

        elif command_list[0] == "SET_TREE_NODE_START":
            max_msg_number = int(command_list[1])

            data = ""
            for i in range(max_msg_number):
                msg = command_mq.receive()[0]
                data += msg

        elif command_list[0] == "SET_TREE_NODE_END":
            
            data = data.decode('utf-8')
            data_list = data.split(SP)

            fullname = data_list[0]


            if tree is not None:
                offset_list = ast.literal_eval(data_list[1])
                sha_hash_list = ast.literal_eval(data_list[2])
                type_list = ast.literal_eval(data_list[3])

                compare_block_list = []
                for i in range(0, len(offset_list)):
                    compare_block = block.Compare_Block()
                    compare_block.offset = offset_list[i]
                    compare_block.sha_hash = sha_hash_list[i]
                    compare_block.type = type_list[i]
                    compare_block_list.append(compare_block)


                path, name = os.path.split(fullname)

                

                size = os.stat(fullname).st_size
                mtime = os.path.getmtime(fullname)
                if os.path.isdir(fullname):
                    type = "d"
                elif os.path.isfile(fullname):
                    type = "f"

                t = createNode(path, name, type, size, mtime)
                t.new_compare_block_list = compare_block_list
                result = tree.addNode(t)


            else:
                if fullname == rootFullName:
                    path, name = os.path.split(rootFullName)
                    size = os.stat(rootFullName).st_size
                    mtime = os.path.getmtime(rootFullName)

                    tree = createNode(path, name, "d", size, mtime)


    return tree

       
def treeSever_initDB():

    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()

        cur.execute("delete from fileinfo")
        db.commit()
        db.close()
        result_mq.send("initDB OK")

    except Exception as e:        
        print(e)
        db.close()
        result_mq.send("initDB Failed")


def treeServer_loadDB():

    tree = None

    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        
        cur.execute("select * from fileinfo")
        for row in cur.fetchall():
            path = row[0]
            name = row[1]
            type = row[2]
            size = int(row[3])
            mtime = float(row[4])
            cb_offset_list = json.loads(row[5])
            cb_sha_list = json.loads(row[6])
            cb_type_list = json.loads(row[7])

            compare_block_list = []
            for i in range(0, len(cb_offset_list)):
                compare_block = block.Compare_Block()
                compare_block.offset = cb_offset_list[i]
                compare_block.sha_hash = cb_sha_list[i]
                compare_block.type = cb_type_list[i]
                compare_block_list.append(compare_block)

            if tree is not None:
                t = createNode(path, name, type, size, mtime)
                t.new_compare_block_list = compare_block_list

                tree.addNode(t)

            else: # Tree is None
                if name == root_name and path == root_path:
                    tree = createNode(path, name, type, size, mtime)
                    tree.new_compare_block_list = compare_block_list

        db.close()
        result_mq.send("loadDB OK")

    except Exception as e:
        print(e)
        tree = None
        db.close()
        result_mq.send("loadDB Failed")

    return tree

def treeServer_saveDB(tree):
    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        tree._saveAllTree(cur)
        db.commit()
        db.close()
        result_mq.send("saveDB OK")

    except Exception as e:
        print(e)
        result_mq.send("saveDB Failed")

def treeServer_main():

    tree = None


    while(1):
        msg = command_mq.receive()[0]
        split_msg = msg.split("|")
        command = split_msg[0]
        print(split_msg)

        if command == "getTree":
            treeServer_getTree(tree)

        elif command == "setTree":
            tree = treeServer_setTree(tree)

        elif command == "initDB":
            treeSever_initDB()
            

        elif command == "saveDB":
            treeServer_saveDB(tree)

           

        elif command == "loadDB":
            tree = treeServer_loadDB()
            
        # elif command == "addFile":
        #     fileFullName = split_msg[1]
        #     size = split_msg[2]
        #     mtime = split_msg[3]

        #     result = tree.addFile(fileFullName, size, mtime)
        #     if result:
        #         result_mq.send("add File OK")
        #     else:
        #         name, path = os.path.split(fileFullName)
        #         result_mq.send("File Not Found - " + path)


        # elif command == "addDir":
        #     dirFullName = split_msg[1]
        #     size = split_msg[2]
        #     mtime = split_msg[3]

        #     result = tree.addDir(dirFullName, size, mtime)
        #     if result:
        #         result_mq.send("add Dir OK")
        #     else:
        #         name, path = os.path.split(dirFullName)
        #         result_mq.send("File Not Found - " + path)


        # elif command == "update":
        #     fullName = split_msg[1]
        #     size = split_msg[2]
        #     mtime = split_msg[3]
        #     result = tree.update(fullName, size, mtime)
        #     if result:
        #         result_mq.send("update OK")
        #     else:
        #         result_mq.send("File Not Found - " + fullName)

        # elif command == "compare":
        #     dTree = makeDiskTree(rootFullName)
        #     dirs, files = dTree.compare(tree)
        
        #     for dir in dirs:
        #         print("changed Dirs : " + os.path.join(dir.path, dir.name))
        #     for file in files:
        #         print("changed Files : " + os.path.join(file.path, file.name))

           # result_mq.send("OK")


    command_mq.close()
    result_mq.close()

if __name__ == '__main__':
    print('---- Tree Server Start ----')
    print("root_path : ", root_path)
    print("root_name : ", root_name)

    treeServer_main()
