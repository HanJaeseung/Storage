import os

import MySQLdb
from configure import *
import configure
from lz4aes import *
import block

import time

def precheck_lz4_bench(fullName):
    file_str_size = os.path.getsize(fullName)
    partition_num = (file_str_size / configure.PARTITION_SIZE) + 1

    pre_isLZ4_List = []
    f = open(fullName)


    for i in range(partition_num):
        #time.sleep(0.5)
        partition_count = i+1

        min_index = i * configure.PARTITION_SIZE 
        if partition_count == partition_num:
            max_index = file_str_size
        else:
            max_index = (i+1)*configure.PARTITION_SIZE

        f.seek(min_index)

        part_str = f.read(max_index - min_index)

        org_size = len(part_str)

        compressed_data = F_lz4(part_str)
        comp_size = len(compressed_data)

        ratio = round(org_size/float(comp_size),4)

        if ratio >= configure.policy_compress_ratio:
            pre_isLZ4_List.append(True)

        else:
            pre_isLZ4_List.append(False)

    f.close()

    return pre_isLZ4_List


def precheck_saveDB(fullName, mtime, compare_block_list, pre_isLZ4_List=[]):
    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        

        path, name = os.path.split(fullName)
        cb_offset_list = []
        cb_sha_list = []
        cb_type_list = []

        confPartionSize = str(configure.PARTITION_SIZE)
        confMaxBlockNum = str(configure.max_block_num)
        confCompRatio = str(configure.policy_compress_ratio)

        for compare_block in compare_block_list:
            cb_offset_list.append(compare_block.offset)
            cb_sha_list.append(compare_block.sha_hash)
            cb_type_list.append(compare_block.type)


        cb_offset_list =  json.dumps(cb_offset_list)
        cb_sha_list =  json.dumps(cb_sha_list)
        cb_type_list =  json.dumps(cb_type_list)
        pre_isLZ4_List = json.dumps(pre_isLZ4_List)

        
        cur.execute("insert into precheck(path, name, mtime, cb_offset_list, cb_sha_list, cb_type_list, isLZ4, confPartionSize, confMaxBlockNum, confCompRatio) values('"+path+"','"+name+"','"+str(mtime)+"','"+cb_offset_list+"','"+cb_sha_list+"','"+cb_type_list+"','"+pre_isLZ4_List+"','"+confPartionSize+"', '" +confMaxBlockNum+"','"+confCompRatio+"') on duplicate key update mtime='"+str(mtime)+"',cb_offset_list='"+cb_offset_list+"',cb_sha_list='"+cb_sha_list+"',cb_type_list='"+cb_type_list+" ',isLZ4='"+pre_isLZ4_List+" ', confPartionSize='"+confPartionSize+"', confMaxBlockNum='"+confMaxBlockNum+"', confCompRatio='"+ confCompRatio+"'")



        db.commit()
        db.close()

    except Exception as e:
        print(e)


def precheck_mtime_All_loadDB(fullNameList):
    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        
        mtimeList = []
        

        for fullName in fullNameList:
            path, name = os.path.split(fullName)

            cur.execute("select mtime from precheck where path='"+path+"' and name='"+name+"'")
            
            mtime = -1.0
            for row in cur.fetchall():
                mtime = float(row[0])

            mtimeList.append(mtime)
            
            
        db.close()
    except Exception as e:
        print(e)
        db.close()

    return mtimeList



def precheck_mtime_loadDB(fullName):
    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        
        path, name = os.path.split(fullName)

        mtime = -1.0

        cur.execute("select mtime from precheck where path='"+path+"' and name='"+name+"'")
        for row in cur.fetchall():
            mtime = float(row[0])
            
            
        db.close()
    except Exception as e:
        print(e)
        db.close()

    return mtime


def precheck_conf_All_loadDB(fullNameList):
    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        
        confPartionSizeList = []
        confMaxBlockNumList = []
        confCompRatioList = []
        

        for fullName in fullNameList:
            path, name = os.path.split(fullName)

            cur.execute("select confPartionSize, confMaxBlockNum, confCompRatio from precheck where path='"+path+"' and name='"+name+"'")
            
            confPartionSize = -1
            confMaxBlockNum = -1
            confCompRatio = -1.0

            for row in cur.fetchall():
                confPartionSize = int(row[0])
                confMaxBlockNum = int(row[1])
                confCompRatio = float(row[2])
               
            confPartionSizeList.append(confPartionSize)
            confMaxBlockNumList.append(confMaxBlockNum)
            confCompRatioList.append(confCompRatio)
            
            
        db.close()
    except Exception as e:
        print(e)
        db.close()


    return confPartionSizeList, confMaxBlockNumList, confCompRatioList

def precheck_conf_loadDB(fullName):
    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        
        path, name = os.path.split(fullName)

        cur.execute("select confPartionSize, confMaxBlockNum, confCompRatio from precheck where path='"+path+"' and name='"+name+"'")

        confPartionSize = -1
        confMaxBlockNum = -1
        confCompRatio = -1.0

        for row in cur.fetchall():
            confPartionSize = int(row[0])
            confMaxBlockNum = int(row[1])
            confCompRatio = float(row[2])
            
            
        db.close()
    except Exception as e:
        print(e)
        db.close()

    return confPartionSize, confMaxBlockNum, confCompRatio


def precheck_isLZ4_loadDB(fullName):
    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        
        path, name = os.path.split(fullName)

        pre_isLZ4_List = []

        cur.execute("select isLZ4 from precheck where path='"+path+"' and name='"+name+"'")
        for row in cur.fetchall():
            pre_isLZ4_List = json.loads(row[0])
            #pre_isLZ4 = str(row[0])
            
            
        db.close()
    except Exception as e:
        print(e)
        db.close()

    return pre_isLZ4_List

def precheck_compareBlockList_loadDB(fullName):
    try:
        db = MySQLdb.connect(host=DB_host,user=DB_user, passwd=DB_pw, db=DB_dbName, charset='utf8')
        cur = db.cursor()
        
        path, name = os.path.split(fullName)

        mtime = -1.0


        cur.execute("select cb_offset_list, cb_sha_list, cb_type_list from precheck where path='"+path+"' and name='"+name+"'")
        for row in cur.fetchall():
            cb_offset_list = json.loads(row[0])
            cb_sha_list = json.loads(row[1])
            cb_type_list = json.loads(row[2])
            
        compare_block_list = []
        for i in range(0, len(cb_offset_list)):
            compare_block = block.Compare_Block()
            compare_block.offset = cb_offset_list[i]
            compare_block.sha_hash = cb_sha_list[i]
            compare_block.type = cb_type_list[i]
            compare_block_list.append(compare_block)


        db.close()
    except Exception as e:
        print(e)
        db.close()



    return compare_block_list
