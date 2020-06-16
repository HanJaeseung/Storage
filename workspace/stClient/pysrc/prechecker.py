# -*- coding: utf-8 -*-
#!/usr/bin/env python3.4
import sys
import os
import json
import time
import datetime

from anchor_block import *
from precheck import *
from configure import *
import configure

import multiprocessing

try:
    if sys.frozen:
        sys.setdefaultencoding("utf-8")
except:
    pass

def Process_Prechecker(queue, changed_number, print_lock):
    while(True):
     
        dataList = queue.get()

        fullName = dataList[0]
        saved_mtime = dataList[1]
        prev_confPartionSize = dataList[2]
        prev_confMaxBlockNum = dataList[3]
        prev_confCompRatio = dataList[4]


        if fullName == "Precheck END":
            break

        confUpdate = False
        if prev_confPartionSize != configure.PARTITION_SIZE:
            confUpdate = True
        if prev_confMaxBlockNum != configure.max_block_num:
            confUpdate = True
        if prev_confCompRatio != configure.policy_compress_ratio:
            confUpdate = True


        try:
            mtime = os.path.getmtime(fullName)
                
            # saved_mtime = precheck_mtime_loadDB(fullName)
            if  ( str(mtime) != str(saved_mtime) ) or confUpdate:
                
                file_size = os.path.getsize(fullName)
                min_block_size = int(file_size / configure.max_block_num)


                # LZ4 Bench
                isLZ4_List = precheck_lz4_bench(fullName)


                # Make Compare Block
                new_anchor_list = Rabin_Karp_anchor(fullName, anchor_size, d, q, min_block_size)
                new_compare_block_list = Rabin_Karp_split(fullName, anchor_size, d, q, new_anchor_list)
                precheck_saveDB(fullName, mtime, new_compare_block_list, isLZ4_List)

                print_lock.acquire()
                print("------------ NEW Block Anchor List ------------")
                print("FileName : " + fullName)
                print("SHA_Hash : " + str([l.sha_hash for l in new_compare_block_list]))
                print("Offset : " + str([l.offset for l in new_compare_block_list]))
                print("Type : " + str([l.type for l in new_compare_block_list]))
                print("isLZ4_List : " + str(isLZ4_List))
                print
                print_lock.release()

                changed_number.value += 1



        except IOError as e:
            print(e)

        except OSError as e:
            print(e)            

       

def prechecker_main():
    manager = multiprocessing.Manager()
    
    queue = multiprocessing.Queue()
    print_lock = multiprocessing.Lock()

    
    while(True):
       
        loadConfigure()
	start = time.time()
    
        p_prechecker = [None for i in range(NUMBER_OF_PRECHECK_PROCESS)]

        s = datetime.datetime.now()
        print("[Precheck Start]" + str(s))

        changed_number = manager.Value('i', 0)
        fullNameList = []

        for i in range(NUMBER_OF_PRECHECK_PROCESS):
            p_prechecker[i] = multiprocessing.Process(target=Process_Prechecker, args=(queue, changed_number, print_lock))
            p_prechecker[i].start()

        for root, dirs, files in os.walk(rootFullName):
            for file in files:
                if len(file) >= 4 and file[-4:] == ".swp":
                    pass

                else:
                    fullName = os.path.join(root, file)
                    fullNameList.append(fullName)
                    #queue.put(fullName)

        mtimeList = precheck_mtime_All_loadDB(fullNameList)
        print(fullNameList)
        confPartionSizeList, confMaxBlockNumList, confCompRatioList = precheck_conf_All_loadDB(fullNameList)

        print(confPartionSizeList) 
        for i in range(len(fullNameList)):
            fullName = fullNameList[i]
            mtime = mtimeList[i]
            prev_confPartionSize = confPartionSizeList[i]
            prev_confMaxBlockNum = confMaxBlockNumList[i]
            prev_confCompRatio = confCompRatioList[i]

            queue.put([fullName, mtime, prev_confPartionSize, prev_confMaxBlockNum, prev_confCompRatio])

        for i in range(NUMBER_OF_PRECHECK_PROCESS):
            queue.put(["Precheck END", "", "", "", ""])

        for i in range(NUMBER_OF_PRECHECK_PROCESS):
            p_prechecker[i].join()

        s = datetime.datetime.now()
        print("[Precheck End] " + str(s) +", Changed DB : " + str(changed_number.value))
        print
	sec = time.time() - start
	times = str(datetime.timedelta(seconds=sec)).split(".")
	times = times[0]
	f = open("time_check.txt", "a")
	f.write(times + '\n')
	f.close()

        time.sleep(prechecker_sec_time_sleep)
                       

if __name__ == '__main__':
    prechecker_main()
        

