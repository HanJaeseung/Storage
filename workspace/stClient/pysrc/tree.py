# -*- coding: utf-8 -*-
import sys
import os
import platform
import MySQLdb
import json
import sysv_ipc
import ast
from anchor_block import *
from precheck import *
from configure import *
import codecs



reload(sys) 
sys.setdefaultencoding('utf-8')

if platform.system() == 'windows':
    separator = '\\'
else:
    separator = '/'

root_path, root_name = os.path.split(rootFullName)

SP = "|0s283hs1|" # data sparator

try:
    command_mq = sysv_ipc.MessageQueue(command_q_id, sysv_ipc.IPC_CREAT, max_message_size=MAX_MSG_SIZE)
    result_mq = sysv_ipc.MessageQueue(result_q_id, sysv_ipc.IPC_CREAT, max_message_size=MAX_MSG_SIZE)
except:
    command_mq = sysv_ipc.MessageQueue(command_q_id)
    result_mq = sysv_ipc.MessageQueue(result_q_id)




class Tree():
    def __init__(self, filename):
        self.name = filename
        self.path = None
        self.type = None
        self.dirs = []
        self.files = []
        self.mtime = None # 수정시간
        self.size = None

        self.transfer_level = None
        self.similarity = 0

        #self.transfer_block_list = []
        self.org_compare_block_list = []
        self.new_compare_block_list = []

        self.transfer_block_offset_list = []
        self.transfer_block_type_list = []
        self.transfer_block_str_list = []
        
        self.pre_isLZ4_List = [] # 새로운 파일일 경우 Prechecker 가 계산해놓은 isLZ4 사용하여 압축여부 판단.


    
    def _addDirs(self, path, dirs_name_list):
        for dir_name in dirs_name_list:
            dirFullName = os.path.join(path, dir_name)

            size = os.stat(dirFullName).st_size
            mtime = os.path.getmtime(dirFullName)
            
            t = createNode(path, dir_name, "d", size, mtime)
            self.dirs.append(t)

    def _addFiles(self, path, files_name_list):
        for file_name in files_name_list:
            fileFullName = os.path.join(path, file_name)

            if len(fileFullName) >= 4 and fileFullName[-4:] == ".swp":
                pass

            else:
                size = os.stat(fileFullName).st_size
                mtime = os.path.getmtime(fileFullName)

                t = createNode(path, file_name, "f", size, mtime)
                self.files.append(t)
    

    # def addDir(self, fullDirName, size, mtime):
    #     path, name = os.path.split(fullDirName)
    #     t = self.find(path)
    #     if t is not None:
    #         dir = createNode(path, name, "d", size, mtime)
    #         t.dirs.append(dir)
    #         return 1

    #     else:
    #         return 0


    # def addFile(self, fullFileName, size, mtime):
    #     path, name = os.path.split(fullFileName)
    #     t = self.find(path)
    #     if t is not None:
    #         file = createNode(path, name, "f", size, mtime)
    #         t.files.append(file)
    #         return 1

    #     else:
    #         return 0

    def addNode(self, node):
        fullname = os.path.join(node.path, node.name)
        path = node.path

        tn = self.find(fullname) # current
        t = self.find(path) #parent

        if t is None:

            return 0

        elif t is not None:
            # New File
            if tn is None:

                if node.type == "f":
                    t.files.append(node)

                elif  node.type == "d":
                    t.dirs.append(node)

            # Update File
            elif tn is not None:
                if node.type == "f":
                    for i, file in enumerate(t.files):
                        if file.path == node.path and file.name == node.name:
                            t.files[i] = node
                            break

                elif  node.type == "d":
                     for i, dir in enumerate(t.dirs):
                        if dir.path == node.path and dir.name == node.name:
                            t.dirs[i] = node
                            break


            return 1

    
    # def update(self, fullName, size, mtime):
    #     path, name = os.path.split(fullFileName)
    #     t = self.find(fullName)
    #     if t is not None:
    #         t.size = size
    #         t.mtime = mtime
    #         return 1

    #     else:
    #         return 0

    def compare(self, tree):
        changedDirNodes = []
        changedFileNodes = []

   #     make_start = time.time()
    #    print("COMPARE AND MAKE COMPARE_BLOCK_LIST")
        self.__comparing(tree, changedDirNodes, changedFileNodes)

     #   make_time = time.time() - make_start
     #   print(make_time)

        changed_number = len(changedDirNodes) + len(changedFileNodes)
        print("[Compare Result] File or Dir Changed : " + str(changed_number))

        return changedDirNodes, changedFileNodes

    def __comparing(self, tree, changedDirNodes, changedFileNodes):
        fullName = os.path.join(self.path, self.name)
        if tree is not None:
            t = tree.find(fullName)
        else:
            t = None

        
        if self.type == "f":

            if t is None:
                saved_mtime = precheck_mtime_loadDB(fullName)
                saved_confPartionSize, saved_confMaxBlockNum, saved_confCompRatio = precheck_conf_loadDB(fullName)
                confUpdate = False
                if saved_confPartionSize != PARTITION_SIZE:
                    confUpdate = True
                if saved_confMaxBlockNum != max_block_num:
                    confUpdate = True
                if saved_confCompRatio != policy_compress_ratio:
                    confUpdate = True

                if  (str(self.mtime) != str(saved_mtime)) or confUpdate:
                    print("[PreCheck Not Find] Make Compare Block !! " + fullName)
                    file_size = os.path.getsize(fullName)
                    min_block_size = int(file_size / max_block_num)

                    new_anchor_list = Rabin_Karp_anchor(fullName, anchor_size, d, q, min_block_size)
                    self.new_compare_block_list = Rabin_Karp_split(fullName, anchor_size, d, q, new_anchor_list)
                    precheck_saveDB(fullName, self.mtime, self.new_compare_block_list)

                else:
                    print("[PreCheck Find] " + fullName)
                    self.new_compare_block_list = precheck_compareBlockList_loadDB(fullName)
                    self.pre_isLZ4_List = precheck_isLZ4_loadDB(fullName)

                self.transfer_level = "File"
                self.similarity = 0



                changedFileNodes.append(self)

            elif t is not None:
                if str(self.mtime) != str(t.mtime) or str(self.size) != str(t.size):

                    self.org_compare_block_list = t.new_compare_block_list

                    saved_mtime = precheck_mtime_loadDB(fullName)
                    
                    if  str(self.mtime) != str(saved_mtime):
                        print("[PreCheck Not Find] Make Compare Block!! " + fullName)
                        
                        file_size = os.path.getsize(fullName)
                        min_block_size = int(file_size / max_block_num)

                        new_anchor_list = Rabin_Karp_anchor(fullName, anchor_size, d, q, min_block_size)
                        self.new_compare_block_list = Rabin_Karp_split(fullName, anchor_size, d, q, new_anchor_list)
                        precheck_saveDB(fullName, self.mtime, self.new_compare_block_list)

                    else:
                        print("[PreCheck Find] " + fullName)
                        self.new_compare_block_list = precheck_compareBlockList_loadDB(fullName)


                    if len(self.org_compare_block_list) == 0:
                        # transfer_block = block.Transfer_Block()
                        # transfer_block.str = text
                        # transfer_block.offset = [0, len(text)]
                        # transfer_block.type = "insert"

                        # self.transfer_block_list.append(transfer_block)
                        self.transfer_level = "File"
                        self.similarity = 0

                    else:
                
                        print("------------ ORG Block Anchor List ------------")
                        print("SHA_Hash : " + str([l.sha_hash for l in self.org_compare_block_list]))
                        print("Offset : " + str([l.offset for l in self.org_compare_block_list]))
                        print("Type : " + str([l.type for l in self.org_compare_block_list]))
                        print

                        print("------------ NEW Block Anchor List ------------")
                        print("SHA_Hash : " + str([l.sha_hash for l in self.new_compare_block_list]))
                        print("Offset : " + str([l.offset for l in self.new_compare_block_list]))
                        print("Type : " + str([l.type for l in self.new_compare_block_list]))
                        print

                    
                        self.similarity = CalcSimilarity(self.new_compare_block_list, self.org_compare_block_list)

                        if self.similarity >= policy_similarity:
                            self.transfer_level = "Block"


                        else:
                            self.transfer_level = "File"


                    changedFileNodes.append(self)
                    
        elif self.type == "d":
            if t is None:
                changedDirNodes.append(self)


        for file in self.files:
            file.__comparing(tree, changedDirNodes, changedFileNodes)

        for dir in self.dirs:
            dir.__comparing(tree, changedDirNodes, changedFileNodes)


    def printAllTree(self):
        self.printTree()

        for file in self.files:
            file.printAllTree()

        for dir in self.dirs:
            dir.printAllTree()

    def printTree(self):
        print("print Tree!!")
        print("     file Name : "+ str(self.name))
        print("     path : " + str(self.path))
        print("     type : " + str(self.type))
        print("     size : " + str(self.size))
        print("     modify Time : " + str(self.mtime))
 #       if self.type == "f":
  #          print("     compare_block_list : ", self.compare_block_list)

        dirs_name = []
        for dir in self.dirs:
            dirs_name.append(dir.name)
        print("     directories : "+ str(dirs_name))

        files_name = []
        for file in self.files:
            files_name.append(file.name)
        print("     files : "+ str(files_name))


    def getTreeNodeList(self):
        node_list = []

        self._getTreeNodeList(node_list)

        return node_list
       

    def _getTreeNodeList(self, node_list):
        node_list.append(self)

        for file in self.files:
            file._getTreeNodeList(node_list)

        for dir in self.dirs:
            dir._getTreeNodeList(node_list)


    def _saveAllTree(self, cur):

        self.__saveTree(cur)

        for file in self.files:
            file._saveAllTree(cur)

        for dir in self.dirs:
            dir._saveAllTree(cur)
    



    def __saveTree(self, cur):
        cb_offset_list = []
        cb_sha_list = []
        cb_type_list = []

        for compare_block in self.new_compare_block_list:
            cb_offset_list.append(compare_block.offset)
            cb_sha_list.append(compare_block.sha_hash)
            cb_type_list.append(compare_block.type)


        cb_offset_list =  json.dumps(cb_offset_list)
        cb_sha_list =  json.dumps(cb_sha_list)
        cb_type_list =  json.dumps(cb_type_list)


        #print(self.path.encode("utf-8"), self.name.encode("utf-8"))
        cur.execute("insert into fileinfo(path, name, type, size, mtime, cb_offset_list, cb_sha_list, cb_type_list) values('"+self.path+"','"+self.name+"','"+self.type+"', '"+str(self.size)+"','"+str(self.mtime)+"','"+cb_offset_list+"','"+cb_sha_list+"','"+cb_type_list+"') on duplicate key update type='" + self.type + "', size='"+str(self.size) +"', mtime='"+str(self.mtime)+"',cb_offset_list='"+cb_offset_list+"',cb_sha_list='"+cb_sha_list+"',cb_type_list='"+cb_type_list+" ' " )





    def find(self, fullName):
        if self.name == os.path.basename(fullName):
            return self

        else:
            fullName = fullName.replace(root_path + separator, "")
            return self.__finding(fullName)


    def __finding(self, fullName):
        splitName = fullName.split(separator)
        depth = len(splitName)
        if depth == 1 and self.name == splitName[-1]:
            return self


        del splitName[0]
        if len(splitName) == 1:
            for i, file in enumerate(self.files):
                if splitName[0] == file.name:
                    return file.__finding(separator.join(splitName))

        for i, dir in enumerate(self.dirs):
            if splitName[0] == dir.name:
                return dir.__finding(separator.join(splitName))




def createNode(path, name, type, size, mtime):
    tree = Tree(name)
    tree.path = path
    tree.type = type
    tree.size = size
    tree.mtime = mtime

    return tree


def makeDiskTree(rootFullName):
    path, name = os.path.split(rootFullName)
    size = os.stat(rootFullName).st_size
    mtime = os.path.getmtime(rootFullName)
    tree = createNode(path, name, "d", size, mtime)

    for root, dirs, files in os.walk(rootFullName):

        dirs.sort()
        files.sort()
        
        t = tree.find(root)
        if t is not None:
            t._addDirs(root, dirs)
            t._addFiles(root, files)


    return tree

def cinterface_Tree_addNode(tree, node):
    tree.addNode(node)

def cinterface_Tree_compare(diskTree, tree):
   changedDirNodes, changedFileNodes = diskTree.compare(tree)
   return [changedDirNodes, changedFileNodes]


def cinterface_Tree_printAllTree(tree):
    tree.printAllTree()


def cinterface_Tree_printTree(tree):
    tree.printTree()

def cinterface_Tree_find(tree, fullName):
    t = tree.find(fullName)
    return t

