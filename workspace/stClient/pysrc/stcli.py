# -*- coding: utf-8 -*-
import sys
import os


from tree import *
from producer import *
from keyManageClient import *
import block
from configure import *
import getpass

from paramiko import SSHClient
import paramiko

try:
    if sys.frozen:
        sys.setdefaultencoding("utf-8")
except:
    pass




def stcli_Start_Prechecker():
    command = "nohup "+client_bin_dir+"/prechecker 1> /dev/null 2>&1 &"
    os.system(command)
    print("[ Start ] prechecker")

def stcli_End_Prechecker():
    command = "killall -9 prechecker"
    os.system(command)
    print("[ Killed ] prechecker")

def stcli_Start_TreeServer():
    command = "nohup "+client_bin_dir+"/treeServer 1> /dev/null 2>&1 &"
    os.system(command)
    print("[ Start ] treeServer")

def stcli_End_TreeServer():
    command = "killall -9 treeServer"
    os.system(command)
    print("[ Killed ] treeServer")

def stcli_Start_Consumer():
    while(True):
        try:
            pswd = getpass.getpass('Password:')

            ssh = SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(HTTP_SERVER,username='root',password=pswd)
            command = "nohup "+server_bin_dir+"/dist/consumer 1> /dev/null 2>&1 &"

            ssh.exec_command(command)
            break
        except:
            print("Permission denied, please try again.")

    print("[ Start ] Consumer")

def stcli_End_Consumer():
    while(True):
        try:
            pswd = getpass.getpass('Password:')
            command = "ssh "+HTTP_SERVER+" killall -9 consumer"
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(HTTP_SERVER,username='root',password=pswd)
            command = "killall -9 consumer"

            ssh.exec_command(command)
            break

        except:
            print("Permission denied, please try again.")

    print("[ Killed ] Consumer")


def stcli_LZ4_Comp(filename):
    f = open(filename, 'r')
    src = f.read()
    f.close()

    compreesed_data = F_lz4(src)

    path, name = os.path.split(filename)

    f = open(name+".lz4", 'w+')
    f.write(compreesed_data)
    f.close()

    print("Write "+name+".lz4")

    

def stcli_LZ4_Decomp(filename):
    f = open(filename, 'r')
    src = f.read()
    f.close()

    decompreesed_data = F_d_lz4(src)

    path, name = os.path.split(filename)

    f = open(name[:-4], 'w+')
    f.write(decompreesed_data)
    f.close()

    print("Write "+name[:-4])

def stcli_AES_Enc(filename):
    f = open(filename, 'r')
    src = f.read()
    f.close()

    temp_aes_key = "Hello World"
    enc_data = F_aes(src, temp_aes_key)

    path, name = os.path.split(filename)

    f = open(name+".enc", 'w+')
    f.write(enc_data)
    f.close()

    print("Write "+name+".enc")

def stcli_AES_Dec(filename):
    f = open(filename, 'r')
    src = f.read()
    f.close()

    temp_aes_key = "Hello World"
    dec_data = F_d_aes(src, temp_aes_key)

    path, name = os.path.split(filename)

    f = open(name[:-4], 'w+')
    f.write(dec_data)
    f.close()

    print("Write "+name[:-4])


def stcli_getTree():
    command_mq.send("getTree")
    tree = None

    while(True):
        command = result_mq.receive()[0]
        command_list = command.split(SP)

        if command_list[0] == "GET_TREE_END":
            print("[getTree] Complete")
            break

        elif command_list[0] == "GET_TREE_NONE":
            tree = None
            break

        elif command_list[0] == "GET_TREE_NODE_START":
            max_msg_number = int(command_list[1])

            data = ""
            for i in range(max_msg_number):
                msg = result_mq.receive()[0]
                data += msg

        elif command_list[0] == "GET_TREE_NODE_END":
            data = data.decode('utf-8')
            data_list = data.split(SP)
        
            name = data_list[0]
            path = data_list[1]
            type = data_list[2]
            mtime = float(data_list[3])
            size = int(data_list[4])
            

            if tree is not None:

                offset_list = ast.literal_eval(data_list[5])
                sha_hash_list = ast.literal_eval(data_list[6])
                type_list = ast.literal_eval(data_list[7])

                compare_block_list = []
                for i in range(0, len(offset_list)):
                    compare_block = block.Compare_Block()
                    compare_block.offset = offset_list[i]
                    compare_block.sha_hash = sha_hash_list[i]
                    compare_block.type = type_list[i]
                    compare_block_list.append(compare_block)

                t = createNode(path, name, type, size, mtime)
                t.new_compare_block_list = compare_block_list

                result = tree.addNode(t)

            else: # Tree is None
                if name == root_name and path == root_path:
                    tree = createNode(path, name, type, size, mtime)

    # if tree is not None:
    #     tree.printAllTree()
    return tree

def stcli_setTreeAll(tree):
    if tree == None:
        return None

    command_mq.send("setTree")

    __stcli_setTreeAll(tree)
    

    command_mq.send("SET_TREE_END"+ SP)

    result = result_mq.receive()[0]
    if result == "SET_TREE_OK":
        print("[setTreeAll] Complete")
        
    else:
        print("[set Tree] Err!")


def __stcli_setTreeAll(tree):

    __stcli_setTreeNode(tree)

    for dirNode in tree.dirs:
        __stcli_setTreeAll(dirNode)

    for fileNode in tree.files:
        __stcli_setTreeAll(fileNode)

def stcli_setTree(changedNode_or_Nodes):

    if changedNode_or_Nodes == None:
        return None
    command_mq.send("setTree")
    filename = None

    if isinstance(changedNode_or_Nodes, list):
        __stcli_setTreeList(changedNode_or_Nodes)

    else:
        filename = os.path.join(changedNode_or_Nodes.path, changedNode_or_Nodes.name)
        __stcli_setTreeNode(changedNode_or_Nodes)

    
    command_mq.send("SET_TREE_END"+ SP)

    result = result_mq.receive()[0]
    if result == "SET_TREE_OK":
        if filename is not None:
            print("[setTree] Complete : " + filename)
        else:
            print("[setTree] Complete!")
    else:
        print("[set Tree] Err!")


def __stcli_setTreeNode(changedNode):

    fullname = os.path.join(changedNode.path, changedNode.name)
    offset_list = [cb.offset for cb in changedNode.new_compare_block_list]
    sha_hash_list = [cb.sha_hash for cb in changedNode.new_compare_block_list]
    type_list = [cb.type for cb in changedNode.new_compare_block_list]

    data = fullname + SP + str(offset_list) + SP + str(sha_hash_list) + SP + str(type_list)

    data = data.encode('utf-8')
    data_size = len(data)
    #data_size = sys.getsizeof(data)

    send_amount = int(round( (data_size / float(MAX_MSG_SIZE) + 0.5)))

    command_mq.send("SET_TREE_NODE_START" + SP + str(send_amount))

    for i in range(send_amount):
        if i == send_amount-1 :
            send_data = data[MAX_MSG_SIZE * i :]
        else:
            send_data = data[MAX_MSG_SIZE * i : MAX_MSG_SIZE * (i + 1)]

        command_mq.send(send_data)

    command_mq.send("SET_TREE_NODE_END"+ SP)



def __stcli_setTreeList(changedNodes=[]):

    if len(changedNodes) == 0:
        print("[SET TREE] Not Changed Tree.")
        return None

    for changedNode in changedNodes:
        __stcli_setTreeNode(changedNode)

def stcli_saveDB():
    command_mq.send("saveDB")
    result = result_mq.receive()[0]
    print(result)

def stcli_initDB():
    command_mq.send("initDB")
    result = result_mq.receive()[0]
    print(result)


def stcli_loadDB():
    command_mq.send("loadDB")
    result = result_mq.receive()[0]
    print(result)

def stcli_send():
    tree = stcli_getTree()
    diskTree = makeDiskTree(rootFullName) #Disk Tree

    changedDirNodes, changedFileNodes = diskTree.compare(tree)
    if len(changedDirNodes) >= 1 or len(changedFileNodes) >= 1:
    
        public_key_string = http_get_rsa_public_key()
        print("[Key Exchange] RSA Get Key")

        enc_AES_key =  rsa_encrypt(AES_key, public_key_string)
        print("[Key Exchange] RSA Encrypt AES Key : " + str(AES_key) + " -> " + str(enc_AES_key))
    
        http_post_aes_private_key(enc_AES_key[0])
        print("[Key Exchange] Encrypt AES Key Send")

        result_dirNodes, result_fileNodes = producer_main(changedDirNodes, changedFileNodes, AES_key)
        print("[Send] Complete!")

        result_nodes = result_dirNodes + result_fileNodes
        stcli_setTree(result_nodes)
        

    else:
        print("[Send] No files to send")

def stcli_find():
    filename = sys.argv[2]
    tree = stcli_getTree()
    if tree is None:
        print("Tree is None.")
        return

    t = tree.find(filename)
    if t is not None:
        t.printTree()
    else:
        print("not Find.")

def stcli_printAll():
    tree = stcli_getTree()
    tree.printAllTree()

def stcli_main(COMMAND):

    changeFiles = []
    tree = None

    if COMMAND == COMMAND_SEND:
        stcli_send()
        
    elif COMMAND == COMMAND_FIND:
        stcli_find()

    elif COMMAND == COMMAND_PRINT_ALL:
        stcli_printAll()

    elif COMMAND == COMMAND_SAVE_DB:
        stcli_saveDB()

    elif COMMAND == COMMAND_INIT_DB:
        stcli_initDB()

    elif COMMAND == COMMAND_LOAD_DB:
        stcli_loadDB()

    elif COMMAND == COMMAND_START_PRECHECKER:
        stcli_Start_Prechecker()

    elif COMMAND == COMMAND_END_PRECHECKER:
        stcli_End_Prechecker()

    elif COMMAND == COMMAND_START_TREESERVER:
        stcli_Start_TreeServer()

    elif COMMAND == COMMAND_END_TREESERVER:
        stcli_End_TreeServer()

    elif COMMAND == COMMAND_START_CONSUMER:
        stcli_Start_Consumer()

    elif COMMAND == COMMAND_END_CONSUMER:
        stcli_End_Consumer()

    elif COMMAND == COMMAND_LZ4_COMP:
        filename = sys.argv[2]
        stcli_LZ4_Comp(filename)

    elif COMMAND == COMMAND_LZ4_DECOMP:
        filename = sys.argv[2]
        stcli_LZ4_Decomp(filename)

    elif COMMAND == COMMAND_AES_ENC:
        filename = sys.argv[2]
        stcli_AES_Enc(filename)

    elif COMMAND == COMMAND_AES_DEC:
        filename = sys.argv[2]
        stcli_AES_Dec(filename)

if __name__ == '__main__':
    COMMAND = sys.argv[1]
    stcli_main(COMMAND)



                
                                
