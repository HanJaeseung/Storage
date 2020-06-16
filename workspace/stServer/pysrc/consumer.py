# -*- coding: utf-8 -*-

from kafka import KafkaConsumer
from kafka import KafkaProducer
import os
import sys
import time
import multiprocessing
import threading
import subprocess
import json
import sysv_ipc
import ast
from keyManageServer import *
from configure import *
from lz4aes import *
from filelock import FileLock




try:
    if sys.frozen:
        sys.setdefaultencoding("utf-8")
except:
    pass


producer_start = None



def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def subprocess_open(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata



def printTime(str, t):
    print(str+'{:02d}:{:02d}:{:02d}'.format(t // 3600, (t % 3600 // 60), t % 60))

def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return subprocess.check_output(['du','-sh', path]).split()[0]#.decode('utf-8')


def Process_recv(pNum, q_ready, q_recv_aes, file_lock):
    producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,  max_request_size=200000000, buffer_memory=200000000)
    consumer = KafkaConsumer(
        bootstrap_servers=kafka_bootstrap_servers,
    )

    consumer.subscribe(['DATA'+str(pNum)])
    
    fileCount = 0
    dirCount = 0

    seperator = "|05D123aedc|"

    q_ready.put("RECV"+str(pNum)+" READY")

    for msg in consumer:

        f = open(log_dir+"/recv_"+str(pNum)+"_log", 'a+')
        f.write("Recv"+ str(pNum)+" 중간결과 : "+  str(dirCount) + ", " +str(fileCount)+"\n")
        f.close()
      #  msg = msg.decode()
        data = msg.value        
        split_data = data.split(seperator)

        command = split_data[0]

        if command == "FILE_START":
            filename = split_data[1].decode('utf-8')
      
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    pass

            # if not os.path.isfile(filename+".sttmp"):
            #     f = open(filename+".sttmp", 'w')
            #     f.close()

            f = open(log_dir+"/recv_"+str(pNum)+"_log", 'a+')
            f.write("FILE_START"+ str(pNum)+" filename : "+  filename +"\n")
            f.close()

        elif command == "PARTITION_START":
            filename = split_data[1]
            file_str_size = split_data[2]
            total_num = split_data[3]

            # Partition
            block_count = split_data[4]
            block_num = split_data[5]
            partition_count = split_data[6]
            partition_num = split_data[7]
            part_src_offset = split_data[8]
            part_dst_offset = split_data[9]
            part_type = split_data[10]
            #part_str = message_list[11]

            isLZ4 = split_data[11]
            isAES = split_data[12]
            transfer_level = split_data[13]
            similarity = split_data[14]


            chunk = ""


            f = open(log_dir+"/recv_"+str(pNum)+"_log", 'a+')
            f.write("BLOCK_START"+ str(pNum)+" filename : "+  filename +"\n")
            f.close()

        elif command == "CHUNK_DATA":
            #chunk += split_data[1]
            chunk += data.partition(seperator)[2]

            f = open(log_dir+"/recv_"+str(pNum)+"_log", 'a+')
            f.write("CHUNK_DATA"+ str(pNum)+" filename : "+  filename +"\n")
            f.close()

        elif command == "PARTITION_END":
            part_str = chunk

            message_list = [filename, file_str_size, total_num, block_count, block_num, partition_count, partition_num, part_src_offset, part_dst_offset, part_type, part_str, isLZ4, isAES, transfer_level, similarity]
            q_recv_aes.put(message_list)
            f = open(log_dir+"/recv_"+str(pNum)+"_log", 'a+')
            f.write("PARTITION_END"+ str(pNum)+" filename : "+  filename +"\n")
            f.close()

            


        elif command == "FILE_END":
            fileCount +=1

            f = open(log_dir+"/recv_"+str(pNum)+"_log", 'a+')
            f.write("FILE_END"+ str(pNum)+" filename : "+  filename +"\n")
            f.close()



        elif command == "MKDIR":

            dirname = split_data[1].decode('utf-8')

            # dirname = dirname.replace('&','\&')

            # print(split_data)
            # print(dirname)



            f = open(log_dir+"/recv_"+str(pNum)+"_log", 'a+')
            f.write("MKDIR"+ str(pNum)+" dirname : "+  dirname +"\n")
            f.close()

            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except OSError as exc: # Guard against race condition
                    pass

            producer.send("COMPLETE", bytes("DIR|") + bytes(dirname.encode('utf-8')))
            dirCount +=1      

            f = open(log_dir+"/recv_"+str(pNum)+"_log", 'a+')
            f.write("MKDIR2"+ str(pNum)+" dirname : "+  dirname +"\n")
            f.close()             
            

        elif command == "PRODUCER_END":
#	    print("PROCESS RECV END"+str(pNum))
            file_lock.acquire()
            f = open(log_dir+"/main_log", 'a+')
            f.write("Recv"+ str(pNum)+" 결과 : "+  str(dirCount) + ", " +str(fileCount)+"\n")
            f.close()
            file_lock.release()

            break

        else:
            print("command not Found !!!!" +  str(split_data))
            file_lock.acquire()
            f = open(log_dir+"/main_log", 'a+')
            f.write("Recv"+ str(pNum)+" Command Not Found : "+ command+"\n")
            f.close()
            file_lock.release()




    producer.close()
    consumer.close()

    


def Process_aes(q_recv_aes, q_aes_lz4, AES_key, file_lock):
    while(True):
        message_list = q_recv_aes.get()
        filename = message_list[0]
#       print("aes q Size  : " + str(q_recv_aes.qsize()))
        
        file_lock.acquire()
        f = open(log_dir+"/main_log", 'a+')
        f.write("aes q Size : " + str(q_recv_aes.qsize())+"\n")
        f.close()
        file_lock.release()

        if filename == "PRODUCER_END":
#            print("PROCESS AES END")
            break	


        # File
        file_str_size = message_list[1]
        total_num = message_list[2]

        # Partition
        block_count = message_list[3]
        block_num = message_list[4]
        partition_count = message_list[5]
        partition_num = message_list[6]
        part_src_offset = message_list[7]
        part_dst_offset = message_list[8]
        part_type = message_list[9]
        part_str = message_list[10]

        isLZ4 = message_list[11]
        isAES = message_list[12]
        transfer_level = message_list[13]
        similarity = message_list[14]


        if part_type == "insert":


            if str2bool(isAES):

                aes_result = F_d_aes(filename, file_lock, part_str, AES_key)
                if aes_result == "-1":
                    pass

                else:
                    part_str = aes_result


        message_list = [filename, file_str_size, total_num, block_count, block_num, partition_count, partition_num, part_src_offset, part_dst_offset, part_type, part_str, isLZ4, isAES, transfer_level, similarity]
        
        q_aes_lz4.put(message_list)



def Process_lz4(q_aes_lz4, q_lz4_writer, file_lock):
    while(True):
        message_list = q_aes_lz4.get()
        filename = message_list[0]

#	print("lz4 q Size : " + str(q_aes_lz4.qsize()))
        file_lock.acquire()
        f = open(log_dir+"/main_log", 'a+')
        f.write("lz4 q Size : " + str(q_aes_lz4.qsize())+"\n")
        f.close()
        file_lock.release()

        if filename == "PRODUCER_END":
#            print("PROCESS LZ4 END")
            break

        # File
        file_str_size = message_list[1]
        total_num = message_list[2]

        # Partition
        block_count = message_list[3]
        block_num = message_list[4]
        partition_count = message_list[5]
        partition_num = message_list[6]
        part_src_offset = message_list[7]
        part_dst_offset = message_list[8]
        part_type = message_list[9]
        part_str = message_list[10]

        isLZ4 = message_list[11]
        isAES = message_list[12]
        transfer_level = message_list[13]
        similarity = message_list[14]

        if part_type == "insert":
          
            if str2bool(isLZ4):
                
                lz4_result = F_d_lz4(filename, file_lock, part_str)

                if lz4_result == "-1":
                    pass
                else:
                    part_str = lz4_result

        message_list = [filename, file_str_size, total_num, block_count, block_num, partition_count, partition_num, part_src_offset, part_dst_offset, part_type, part_str, isLZ4, isAES, transfer_level, similarity]
        q_lz4_writer.put(message_list)






def Process_Writer(q_lz4_writer, print_lock, file_lock, part_count_lock, part_count_dict):
    producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,  max_request_size=200000000, buffer_memory=200000000)
    
    while(True):
        message_list = q_lz4_writer.get()
        filename = message_list[0]
        

        file_lock.acquire()
        f = open(log_dir+"/main_log", 'a+')
        f.write("writer q Size : " + str(q_lz4_writer.qsize())+"\n")
        f.close()
        file_lock.release()

        if filename == "PRODUCER_END":
            break
            
        # File
        file_str_size = message_list[1]
        total_num = message_list[2]

        # Partition
        block_count = message_list[3]
        block_num = message_list[4]
        partition_count = message_list[5]
        partition_num = message_list[6]
        part_src_offset = message_list[7]
        part_dst_offset = message_list[8]
        part_type = message_list[9]
        part_str = message_list[10]

        isLZ4 = message_list[11]
        isAES = message_list[12]
        transfer_level = message_list[13]
        similarity = message_list[14]


        part_count_lock.acquire()
        if filename not in part_count_dict:
            cur_part_count = 0
            part_count_dict[filename] = 0
            f = open(filename+".sttmp", "w")
            if int(file_str_size) != 0:
                f.seek(int(file_str_size)-1)
                f.write("\0")
            f.close()
        part_count_lock.release()
        
        

        


        part_src_offset = ast.literal_eval(part_src_offset)
        part_dst_offset = ast.literal_eval(part_dst_offset)

        if part_type == "insert":
            with FileLock(filename+".sttmp", timeout=600):
                f = open(filename+".sttmp", "r+t")
                f.seek(int(part_dst_offset[0]))
                f.write(part_str)
                f.close()

                cur_part_count = part_count_dict[filename] + 1
                part_count_dict[filename] = cur_part_count

            

        elif part_type == "update":
            f = open(filename, "r")
            f.seek(int(part_src_offset[0]))
            src_str = f.read(int(part_src_offset[1]) - int(part_src_offset[0]))
            f.close()

            with FileLock(filename+".sttmp", timeout=600):
                f = open(filename+".sttmp", "r+t")
                f.seek(int(part_dst_offset[0]))
                f.write(src_str)
                f.close()

                cur_part_count = part_count_dict[filename] + 1
                part_count_dict[filename] = cur_part_count
        
        
        print_lock.acquire()
        print("-------BLOCK-------")
        print("FILE NAME : " + filename)
        print("TOTAL_NUM : " + str(cur_part_count) +"/"+ str(total_num))
        print("BLOCK COMMAND : " + part_type)
        print("BLOCK SRC OFFSET : " + str(part_src_offset))
        print("BLOCK DST OFFSET : " + str(part_dst_offset))
        print("BLOCK LEN : " + str(len(part_str)))
        print("isLZ4 : " + str(isLZ4))
        print("isAES : " + str(isAES))
        print("Similarity : " + str(similarity))
        print("TransferLevel : " + transfer_level)
        print 
        print_lock.release()

        if cur_part_count == int(total_num):
            filename = filename.replace('&','\&')
            producer.send("COMPLETE", bytes("FILE|") + bytes(filename.encode('utf-8')))
            os.system("rm -rf " + filename)
            # filename = filename.replace('&','\&')
            os.system("mv " + filename + ".sttmp " + filename)

           # os.system("rm -rf " + filename + ".sttmp")



    producer.close()




   
def consumer_main():
    print("consumer start")
    try:
            key_mq = sysv_ipc.MessageQueue(ipc_key_queue_id, sysv_ipc.IPC_CREAT, max_message_size=MAX_MSG_SIZE)
    except:
        pass

    consumer_start = time.time()

    print(kafka_bootstrap_servers)
    consumer = KafkaConsumer(
    bootstrap_servers=kafka_bootstrap_servers,
    # auto_offset_reset='earliest'
    )
    consumer.subscribe(['STATUS'])

    producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,  max_request_size=200000000, buffer_memory=200000000)


    p_http_server = multiprocessing.Process(target=HTTP_Server_main, args=())
    p_http_server.start()

    for msg in consumer:
     
        data = msg.value
        split_data = data.split("|")
        command = split_data[0]

        if command == "PRODUCER_START":
	    print("consumer check1")
            consumer_start = time.time()
            producer_start = split_data[1]
            NUMBER_OF_RECV_PROCESS = int(split_data[2])
	    print("consumer check1.1")

            AES_key = key_mq.receive()[0]

	    print("consumer check1.2")

            # process create

            q_ready = multiprocessing.Queue()
            q_recv_aes = multiprocessing.Queue()
            q_aes_lz4 = multiprocessing.Queue()
            q_lz4_writer = multiprocessing.Queue()
	    print("consumer check1.5")

            print_lock = multiprocessing.Lock()
            file_lock = multiprocessing.Lock()
            part_count_lock = multiprocessing.Lock()

            manager = multiprocessing.Manager()
            part_count_dict = manager.dict()
            
          
	    print("consumer check2")

            p_recv = [None for i in range(NUMBER_OF_RECV_PROCESS)]
            for i in range(0, NUMBER_OF_RECV_PROCESS):
                p_recv[i] = multiprocessing.Process(target=Process_recv, args=(i, q_ready, q_recv_aes, file_lock))
                #p_recv[i] = threading.Thread(target=Process_recv, args=(i, q_ready, q_recv_aes, file_lock))
                p_recv[i].start()



            p_aes = [None for i in range(NUMBER_OF_AES_PROCESS)]
            for i in range(NUMBER_OF_AES_PROCESS):
                p_aes[i] = multiprocessing.Process(target=Process_aes, args=(q_recv_aes, q_aes_lz4, AES_key, file_lock))
                p_aes[i].start()


            p_lz4 = [None for i in range(NUMBER_OF_LZ4_PROCESS)]
            for i in range(NUMBER_OF_LZ4_PROCESS):
                p_lz4[i] = multiprocessing.Process(target=Process_lz4, args=(q_aes_lz4,q_lz4_writer, file_lock))
                p_lz4[i].start()

            writer_start = time.time()
            p_writer = [None for i in range(NUMBER_OF_WRITER_PROCESS)]
            for i in range(NUMBER_OF_WRITER_PROCESS):
                p_writer[i] = multiprocessing.Process(target=Process_Writer, args=(q_lz4_writer, print_lock, file_lock, part_count_lock, part_count_dict))
                #p_writer[i] = threading.Thread(target=Process_Writer, args=(q_lz4_writer, print_lock, file_lock))
                p_writer[i].start()

	    print("consumer check3")

            # READY
            for i in range(NUMBER_OF_RECV_PROCESS):
                q_ready.get()

            producer.send("RESPONSE", bytes("CONSUMER_READY"))


            # join
            for i in range(NUMBER_OF_RECV_PROCESS):
                p_recv[i].join()
           # print("[RECV] END")

            producer.send("COMPLETE", bytes("ALL_DIR_COMPLETE|"))
            
            for i in range(NUMBER_OF_AES_PROCESS):
                message_list = ["PRODUCER_END"]
                q_recv_aes.put(message_list)

            for i in range(NUMBER_OF_AES_PROCESS):
                p_aes[i].join()
          #  print("[AES] END")

            for i in range(NUMBER_OF_LZ4_PROCESS):
                message_list = ["PRODUCER_END"]
                q_aes_lz4.put(message_list)

            for i in range(NUMBER_OF_LZ4_PROCESS):
                p_lz4[i].join()
          #  print("[LZ4] END")

            for i in range(NUMBER_OF_WRITER_PROCESS):
                message_list = ["PRODUCER_END"]
                q_lz4_writer.put(message_list)

            for i in range(NUMBER_OF_WRITER_PROCESS):
                p_writer[i].join()
          #  print("[COMBINE] END")    
            writer_end = time.time() - writer_start
            f = open("writer_time", "a")
            f.write(str(writer_end) + "\n")
            f.close()

            producer.send("COMPLETE", bytes("ALL_FILE_COMPLETE|"))

            
            totalTime = int(time.time() - float(producer_start))

            print("-------------RECV END!!------------")
            printTime("Total Time : ", totalTime)

        elif command == "PRODUCER_ENDED":
            pass

    p_http_server.join()


	

if __name__ == '__main__':
    consumer_main()
    

