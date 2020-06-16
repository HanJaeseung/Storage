# -*- coding: utf-8 -*-
import sys
import os
import time
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import threading
import multiprocessing
import subprocess

from anchor_block import *

from lz4aes import *

import block
from configure import *


kafka_bootstrap_servers = kafka_server + ":" + kafka_port

producer_start = None

def str2bool(v):
    if type(v) == bool:
        return v

    return v.lower() in ("yes", "true", "t", "1")

def subprocess_open(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata


def sendMsg(producer, topic, msg):
    # while(True):
    #     future = producer.send(topic, bytes(msg))
    #     #producer.flush()
    #     try:
    #         record_metadata = future.get(timeout=60)
    #         break
    #     except KafkaError as e:
    #         # Decide what to do if produce request failed...
    #         f = open(log_dir+"/main_log", 'a+')
    #         f.write(str(e) +"\n")
    #         f.close()

    producer.send(topic, bytes(msg))
    
            


def printTime(str, t):
    print(str+'{:02d}:{:02d}:{:02d}'.format(t // 3600, (t % 3600 // 60), t % 60))


def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return subprocess.check_output(['du','-sh', path]).split()[0]#.decode('utf-8')



def Process_lz4(q_main_lz4, q_lz4_aes, file_lock):
    lock_state = -1
    while(True):
        # if lock_state == -1:
        #     q_main_lz4_output_lock.acquire()
        # lock_state = 1
        message_list = q_main_lz4.get()
   
        command = message_list[0]

        if command == "PRODUCER_END":
            # lock_state = -1
            # q_main_lz4_output_lock.release()
            break
        
        elif command == "DIR":
            # lock_state = -1
            # q_main_lz4_output_lock.release()
            q_lz4_aes.put(message_list)

        elif command == "FILE":

            filename = message_list[1]
            file_str_size = message_list[2]
            total_num = message_list[3]
            block_count = message_list[4]
            block_num = message_list[5]

            partition_count = message_list[6]
            partition_num = message_list[7]

            part_src_offset = message_list[8]
            part_dst_offset = message_list[9]
            part_type = message_list[10]
            part_str = message_list[11]

            pre_isLZ4 = message_list[12]
            transfer_level = message_list[13]
            similarity = message_list[14]

   
            # if block_count == block_num and partition_count == partition_num:
            #     lock_state = -1
            #     q_main_lz4_output_lock.release()

            
            if str2bool(default_LZ4):
                if part_type == "insert":

                    # 수정된 파일인 경우 블록별 데이터 직접 압축 후 판단.
                    if pre_isLZ4 == "-1":
                        org_size = len(part_str)

                        compressed_str = F_lz4(part_str)
                        lz4_size = len(compressed_str)
                      #  del compressed_str


                        ratio = round(org_size/float(lz4_size),4)
                      #  del lz4_size
                        
                        if ratio >= policy_compress_ratio:
                            part_str = F_lz4(part_str)
                            isLZ4 = True

                        else:
                            isLZ4 = False

                       # del ratio

                    # 새로운 파일이며, prechcker에 의해 이미 압축 판단된 경우 True
                    elif str2bool(pre_isLZ4):
                        #print("[PreChecking LZ4]"+ str(filename.encode("utf-8")))
                        part_str =  F_lz4(part_str)
                        isLZ4 = True

                    # 새로운 파일이며, prechcker에 의해 이미 압축 판단된 경우 False
                    else:
                        #print("[PreChecking Not LZ4]"+ str(filename.encode("utf-8")))
                        isLZ4 = False
                    
                else:
                    isLZ4 = False
                    
            else:
                isLZ4 = False


            message_list = [command, filename, file_str_size, total_num, block_count, block_num, partition_count, partition_num, part_src_offset, part_dst_offset, part_type, part_str, isLZ4, transfer_level, similarity]
            q_lz4_aes.put(message_list)

            file_lock.acquire()
            f = open(log_dir+"/main_log", 'a+')
            f.write("lz4 q Size : " + str(q_main_lz4.qsize())+"\n")
            f.close()
            file_lock.release()



def Process_aes(q_lz4_aes, q_aes_send, AES_key, file_lock):
    global default_AES
    lock_state = -1
    while(True):
        # if lock_state == -1:
        #     q_lz4_aes_output_lock.acquire()
        # lock_state = 1

        message_list = q_lz4_aes.get()
        command = message_list[0]

        if command == "PRODUCER_END":
            # lock_state = -1
            # q_lz4_aes_output_lock.release()
            break

        elif command == "DIR":
            # lock_state = -1
            # q_lz4_aes_output_lock.release()
            q_aes_send.put(message_list)
            

        elif command == "FILE":
            filename = message_list[1]
            file_str_size = message_list[2]
            total_num = message_list[3]
            block_count = message_list[4]
            block_num = message_list[5]
            partition_count = message_list[6]
            partition_num = message_list[7]
            part_src_offset = message_list[8]
            part_dst_offset = message_list[9]
            part_type = message_list[10]
            part_str = message_list[11]
            isLZ4 = message_list[12]
            transfer_level = message_list[13]
            similarity = message_list[14]

            # if block_count == block_num and partition_count == partition_num:
            #     q_lz4_aes_output_lock.release()
            

            if str2bool(default_AES):
                if part_type == "insert":
                    part_str = F_aes(part_str, AES_key)
                    isAES = True

                else:
                    isAES = False

            else:    
                 isAES = False

            message_list = [command, filename, file_str_size, total_num, block_count, block_num, partition_count, partition_num, part_src_offset, part_dst_offset, part_type, part_str, isLZ4, isAES, transfer_level, similarity]

            q_aes_send.put(message_list)

            file_lock.acquire()
            f = open(log_dir+"/main_log", 'a+')
            f.write("aes q Size : " + str(q_lz4_aes.qsize())+"\n")
            f.close()
            file_lock.release()





def Process_send(pNum, q_aes_send, file_lock, part_count_lock, part_count_dict):
    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers,
        max_request_size=200000000,
        #buffer_memory=200000000,
        acks='all',
        request_timeout_ms=60000)
    

    dirCount =0
    fileCount = 0

    file_lock.acquire()
    f = open(log_dir+"/main_log", 'a+')
    f.write("Send"+ str(pNum)+" Ready\n")
    f.close()
    file_lock.release()


    lock_state = -1
    while(True):
        # if lock_state == -1:
        #     q_aes_send_output_lock.acquire()
        # lock_state = 1

        message_list = q_aes_send.get()
        command = message_list[0]

        seperator = "|05D123aedc|"

        
         #print("send q Size : " + str(q_inter2_send.qsize()))
        if command == "PRODUCER_END":
            # lock_state = -1
            # q_aes_send_output_lock.release()
            sendMsg(producer, 'DATA'+str(pNum), "PRODUCER_END")
          
            file_lock.acquire()
            f = open(log_dir+"/main_log", 'a+')
            f.write("Send"+ str(pNum)+" 결과 : "+  str(dirCount) + ", " +str(fileCount)+"\n")
            f.close()
            file_lock.release()

            break

        elif command == "DIR":
            # lock_state = -1
            # q_aes_send_output_lock.release()
            dirname = message_list[1]
            sendMsg(producer, 'DATA'+str(pNum), bytes("MKDIR"+seperator)+bytes(dirname.encode('utf-8')))
           
            print("[SEND] " + dirname.encode("utf-8"))
            dirCount +=1

            f = open(log_dir+"/send_"+str(pNum)+"_log", 'a+')
            f.write("MKDIR"+ str(pNum)+" dirname : "+  dirname.encode("utf-8") +"\n")
            f.close()

        elif command == "FILE":
            # File
            filename = message_list[1]
            file_str_size = message_list[2]
            total_num = message_list[3]

            # Partition
            block_count = message_list[4]
            block_num = message_list[5]
            partition_count = message_list[6]
            partition_num = message_list[7]
            part_src_offset = message_list[8]
            part_dst_offset = message_list[9]
            part_type = message_list[10]
            part_str = message_list[11]

            isLZ4 = message_list[12]
            isAES = message_list[13]
            transfer_level = message_list[14]
            similarity = message_list[15]


            part_count_lock.acquire()
            if filename not in part_count_dict:
                cur_part_count = 1
                part_count_dict[filename] = 1
                sendMsg(producer, 'DATA'+str(pNum), bytes("FILE_START"+seperator) + bytes(filename))
                f = open(log_dir+"/send_"+str(pNum)+"_log", 'a+')
                f.write("FILE_START"+ str(pNum)+" filename : "+  filename.encode("utf-8") +"\n")
                f.close()

            else:
                cur_part_count = part_count_dict[filename] + 1
                part_count_dict[filename] = cur_part_count

            part_count_lock.release()

            # if block_count == block_num and partition_count == partition_num:
            #     q_aes_send_output_lock.release()

            
            # if block_count == 1 and partition_count == 1:
            #     sendMsg(producer, 'DATA'+str(pNum), bytes("FILE_START|05D123aedc|") + bytes(filename.encode('utf-8')))
            
            # f = open(log_dir+"/send_"+str(pNum)+"_log", 'a+')
            # f.write("BLOCK_START"+ str(pNum)+" filename : "+  filename.encode("utf-8") +"\n")
            # f.close()
            
         
            
            partition_header = str(filename) + seperator + str(file_str_size) + seperator + str(total_num) + seperator + str(block_count) + seperator + str(block_num) + seperator + str(partition_count) + seperator + str(partition_num) + seperator + str(part_src_offset) + seperator + str(part_dst_offset) + seperator + str(part_type) + seperator + str(isLZ4) + seperator + str(isAES) + seperator + str(transfer_level) + seperator + str(similarity)
            partition_message = str(part_str)

            #partition_message = part_type + "|02A1Jes3zq|" + str(part_offset) + "|02A1Jes3zq|" + part_str#.encode("utf-8")

            remain_size = len(partition_message)
        
            sendMsg(producer, 'DATA'+str(pNum), bytes("PARTITION_START"+seperator) + bytes(partition_header))
            
            f = open(log_dir+"/send_"+str(pNum)+"_log", 'a+')
            f.write("PARTITION_START"+ str(pNum)+" filename : "+  filename.encode("utf-8") +"\n")
            f.close()

            pos = 0
            while(remain_size):
                read_size = min(CHUNK_SIZE, remain_size)
                #read_size = remain_size
                chunk_data = partition_message[pos : pos + read_size]
                pos = pos + read_size
                remain_size -= read_size

                sendMsg(producer, 'DATA'+str(pNum), bytes("CHUNK_DATA|05D123aedc|")+ bytes(chunk_data))

                f = open(log_dir+"/send_"+str(pNum)+"_log", 'a+')
                f.write("CHUNK_DATA"+ str(pNum)+" filename : "+  filename.encode("utf-8") +"\n")
    
            f.close()

            sendMsg(producer, 'DATA'+str(pNum), bytes("PARTITION_END|05D123aedc|"))
        
            f = open(log_dir+"/send_"+str(pNum)+"_log", 'a+')
            f.write("PARTITION_END"+ str(pNum)+" filename : "+  filename.encode("utf-8") +"\n")
            f.close()

            # sendMsg(producer, 'DATA'+str(pNum), bytes("FILE_END"))
          
            f = open(log_dir+"/send_"+str(pNum)+"_log", 'a+')
            f.write("FILE_END"+ str(pNum)+" filename : "+  filename.encode("utf-8") +"\n")
            f.close()
            if cur_part_count == total_num:
                print("[SEND] " + filename)
                fileCount += 1
                sendMsg(producer, 'DATA'+str(pNum), bytes("FILE_END"))

   
        file_lock.acquire()
        f = open(log_dir+"/main_log", 'a+')
        f.write("send q Size : " + str(q_aes_send.qsize())+"\n")
        f.close()
        file_lock.release()


    producer.close()


def producer_setTree(changedDirNodes, chagnedFileNodes, result_dir_q, result_file_q):
    consumer = KafkaConsumer(bootstrap_servers=kafka_bootstrap_servers)
    consumer.subscribe(['COMPLETE'])

    dir_index_list = []
    file_index_list = []
    count = 0
    for response in consumer:
        split_data = response.value.split("|")
        command = split_data[0]
        count+=1

        
        if command == "FILE":

            
            fileFullname = split_data[1].decode('utf-8')

            path, name = os.path.split(fileFullname)

            for i, chagnedFileNode in enumerate(chagnedFileNodes):
                if chagnedFileNode.name == name and chagnedFileNode.path == path:
                    file_index_list.append(i)
                    
                    break

        elif command == "DIR":


            fileFullname = split_data[1].decode('utf-8')

            path, name = os.path.split(fileFullname)

            for i, chagnedDirNode in enumerate(changedDirNodes):
     
                if chagnedDirNode.name == name and chagnedDirNode.path == path:
                    dir_index_list.append(i)

                    
                    break

        elif command == "ALL_DIR_COMPLETE":
            dir_index_list = sorted(dir_index_list)
            result_dir_q.put(dir_index_list)
            # for index in dir_index_list:
            #     result_dir_q.put(index)
              #  pass
            print("ALL_DIR_COMPLETE", len(dir_index_list))

        elif command == "ALL_FILE_COMPLETE":
            file_index_list = sorted(file_index_list)
            result_file_q.put(file_index_list)
            # for index in file_index_list:
            #     result_file_q.put(index)
              #  pass

            print("ALL_FILE_COMPLETE", len(file_index_list))


           # print("ALL_COMPLETE", count)
            break

    consumer.close()
    return


    

def producer_main(changedDirNodes, changedFileNodes, AES_key):

    if not (len(changedDirNodes) >= 1 or len(changedFileNodes) >= 1):
        print("There is Nothing Send !")
        return [], []

    org_text_size = 0
    block_text_size =  0

    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers)

    consumer = KafkaConsumer(
        bootstrap_servers=kafka_bootstrap_servers)

    consumer.subscribe(['RESPONSE'])

    changedNodes = changedDirNodes + changedFileNodes


    q_main_lz4 = multiprocessing.Queue(policy_max_queue_size)
    q_lz4_aes = multiprocessing.Queue(policy_max_queue_size)
    q_aes_send = multiprocessing.Queue(policy_max_queue_size)
    result_dir_q = multiprocessing.Queue(policy_max_queue_size)
    result_file_q = multiprocessing.Queue(policy_max_queue_size)

    file_lock = multiprocessing.Lock()
    part_count_lock = multiprocessing.Lock()

    manager = multiprocessing.Manager()
    part_count_dict = manager.dict()


    p_setTree = multiprocessing.Process(target=producer_setTree, args=(changedDirNodes, changedFileNodes, result_dir_q, result_file_q))
    p_setTree.start()
    
    p_lz4 = [None for i in range(NUMBER_OF_LZ4_PROCESS)]
    for i in range(NUMBER_OF_LZ4_PROCESS):

        p_lz4[i] = multiprocessing.Process(target=Process_lz4, args=(q_main_lz4, q_lz4_aes, file_lock))
        p_lz4[i].start()


    p_aes = [None for i in range(NUMBER_OF_AES_PROCESS)]
    for i in range(NUMBER_OF_AES_PROCESS):
        p_aes[i] = multiprocessing.Process(target=Process_aes, args=(q_lz4_aes, q_aes_send, AES_key, file_lock))
        p_aes[i].start()


    p_send = [None for i in range(NUMBER_OF_SEND_PROCESS)]
    for i in range(NUMBER_OF_SEND_PROCESS):
        p_send[i] = multiprocessing.Process(target=Process_send, args=(i, q_aes_send, file_lock, part_count_lock, part_count_dict))
        #p_send[i] = threading.Thread(target=Process_send, args=(i, q_aes_send, file_lock))
        p_send[i].start()





    producer_start = time.time()
    producer.send("STATUS",  bytes("PRODUCER_START|"+str(producer_start)+"|"+str(NUMBER_OF_SEND_PROCESS)))
     
    for response in consumer:
	print(response)
        if response.value == "CONSUMER_READY":
            break
    


    for changedDirNode in changedDirNodes:
        DirFullName = os.path.join(changedDirNode.path, changedDirNode.name)
        message_list = ["DIR", DirFullName]
        q_main_lz4.put(message_list)
        #del message_list[:]

    for changedFileNode in changedFileNodes:

        FileFullName = os.path.join(changedFileNode.path, changedFileNode.name)

        org_text_size += os.path.getsize(FileFullName)
        
        pre_isLZ4_List = changedFileNode.pre_isLZ4_List
        transfer_level = changedFileNode.transfer_level
        similarity = changedFileNode.similarity

        file_str_size = os.path.getsize(FileFullName)
        if transfer_level =="File":
            
            partition_num = (file_str_size / PARTITION_SIZE) + 1
            block_count = 1
            block_num = 1

            block_offset = [0, file_str_size]
            block_type = "insert"

            total_num = partition_num

            for i in range(partition_num):
                try:
                    pre_isLZ4 = pre_isLZ4_List[i]
                except:
                    pre_isLZ4 = "-1"


                partition_count = i+1

                min_index = i * PARTITION_SIZE 
                if partition_count == partition_num:
                    max_index = file_str_size
                else:
                    max_index = (i+1)*PARTITION_SIZE

                f = open(FileFullName)
                f.seek(min_index)
                part_str = f.read(max_index - min_index)
                f.close()

                #part_str = block_str[min_index:max_index]
                part_src_offset = []
                part_dst_offset = [min_index, max_index]
                part_type = block_type

                block_text_size += len(part_str) # 디버깅용

                message_list = ["FILE", FileFullName, file_str_size, total_num, block_count, block_num, partition_count, partition_num, part_src_offset, part_dst_offset, part_type, part_str, pre_isLZ4, transfer_level, similarity]
       
                q_main_lz4.put(message_list)


                #del file_str

        elif transfer_level == "Block":
            transfer_insert_list, transfer_update_list = BlockListCompare(FileFullName, changedFileNode.new_compare_block_list, changedFileNode.org_compare_block_list)
            transfer_sorted_list = reMakeBlock(transfer_insert_list, transfer_update_list)
            
            total_num = 0
            
            pre_isLZ4 = "-1"
            for i in range(len(transfer_sorted_list)):

                block_str = transfer_sorted_list[i].str
                
                block_count = i+1
                block_num = len(transfer_sorted_list)

                block_str_size = len(block_str)
                partition_num = (block_str_size / PARTITION_SIZE) + 1

                total_num += partition_num

            for i in range(len(transfer_sorted_list)):
                block_src_offset = transfer_sorted_list[i].src_offset
                block_dst_offset = transfer_sorted_list[i].dst_offset

                block_type = transfer_sorted_list[i].type
                block_str = transfer_sorted_list[i].str
                
                block_count = i+1
                block_num = len(transfer_sorted_list)

                block_str_size = len(block_str)
                partition_num = (block_str_size / PARTITION_SIZE) + 1


                for j in range(partition_num):
                    partition_count = j +1

                    if block_type == "insert":

                        min_index = j * PARTITION_SIZE 
                        if partition_count == partition_num:

                            max_index = block_str_size
                        else:
                            max_index = (j+1)*PARTITION_SIZE

                        part_str = block_str[min_index:max_index]
                        part_src_offset = []
                        part_dst_offset = [block_dst_offset[0] + min_index, block_dst_offset[0] + max_index]

                        part_type = block_type


                    elif block_type == "update":
                        part_str = ""

                        min_index = j * PARTITION_SIZE 
                        if partition_count == partition_num:
                            max_index = block_src_offset[1] - block_src_offset[0]
                        else:
                            max_index = (j+1)*PARTITION_SIZE

                        
                        part_src_offset = [block_src_offset[0] + min_index, block_src_offset[0] + max_index]
                        part_dst_offset = [block_dst_offset[0] + min_index, block_dst_offset[0] + max_index]

                        part_type = block_type

                    
                   


                    block_text_size += len(part_str) # 디버깅용 
                    message_list = ["FILE", FileFullName, file_str_size, total_num, block_count, block_num, partition_count, partition_num, part_src_offset, part_dst_offset, part_type, part_str, pre_isLZ4, transfer_level, similarity]
           
                    q_main_lz4.put(message_list)

            
            #del file_str

    
    lz4_start = time.time()
     # END PRODUCER 
    for i in range(NUMBER_OF_LZ4_PROCESS):
        message_list = ["PRODUCER_END"]
        q_main_lz4.put(message_list)
        #del message_list[:]

    for i in range(NUMBER_OF_LZ4_PROCESS):
        p_lz4[i].join()
    
    lz4_sec = time.time() - lz4_start
    lz4_times = str(datetime.timedelta(seconds=lz4_sec)).split(".")
    lz4_times = lz4_times[0]

    f = open("lz4_time","a")
    f.write(str(lz4_sec) + "\n")
    f.close()


    aes_start = time.time()
    for i in range(NUMBER_OF_AES_PROCESS):
        message_list = ["PRODUCER_END"]
        q_lz4_aes.put(message_list)
        #del message_list[:]

    for i in range(NUMBER_OF_AES_PROCESS):
        p_aes[i].join()

    aes_sec = time.time() - aes_start
    aes_times = str(datetime.timedelta(seconds=aes_sec)).split(".")
    aes_times = aes_times[0]

    f = open("aes_time","a")
    f.write(str(aes_sec) + "\n")
    f.close()

    send_start = time.time()
    for i in range(NUMBER_OF_SEND_PROCESS):
        message_list = ["PRODUCER_END"]
        q_aes_send.put(message_list)
        #del message_list[:]

    for i in range(NUMBER_OF_SEND_PROCESS):
        p_send[i].join()

    send_sec = time.time() - send_start
    send_times = str(datetime.timedelta(seconds=send_sec)).split(".")
    send_times = send_times[0]

    f = open("send_time","a")
    f.write(str(send_sec) + "\n")
    f.close()



    totalTime = int(time.time() - float(producer_start))

    print("-------------SEND END!!------------")
    printTime("Total Time : ", totalTime)


    p_setTree.join()



    
    result_dir = []
    result_file = []

    for i in range(result_dir_q.qsize()):
        dir_index_list = result_dir_q.get()
        for dir_index in dir_index_list:
            result_dir.append(changedDirNodes[dir_index])

    for i in range(result_file_q.qsize()):
        file_index_list = result_file_q.get()
        for file_index in file_index_list:
            result_file.append(changedFileNodes[file_index])
      
    consumer.close()
    producer.close()


    # DEBUG FILE SIZE
    ratio = round((block_text_size / float(org_text_size)) * 100, 2)

    print("Compare Used Block Size in File")
    print("--------------------------------------")
    print("FILE SIZE : "+ str(org_text_size))
    print("BLOCK SIZE : "+ str(block_text_size))
    print("--------------------------------------")
    print("RATIO : " + str(ratio) + " %")
    print("--------------------------------------")


    return result_dir, result_file


def cinterface_producer_main(changedDirNodes, changedFileNodes, AES_key):
    result_dir, result_file = producer_main(changedDirNodes, changedFileNodes, AES_key)
    return [result_dir, result_file]


