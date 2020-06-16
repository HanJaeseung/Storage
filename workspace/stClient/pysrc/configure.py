import json
import sys
import os

def searchConfig():
    configFilePath = None
  
    cwd = os.environ['KETI_STCLIENT_HOME'] + "/conf/client_configure"
    if os.path.exists(cwd):
        configFilePath = cwd
        print("Config Use.. " + configFilePath)
        return configFilePath
    else:
        print("Can't Search Config File")
        return None



def loadConfigure():
    # Python
    try:
        path, name = os.path.split(sys.argv[0])
        if path == "":
            path ="."

        configure_fullname = path + "/../conf/client_configure"

    # C
    except:
        configure_fullname = "../../conf/client_configure"
    # configure_fullname = searchConfig()

    try:
        
        open_json = open(configure_fullname, 'r')
        print("Using config : "+ configure_fullname)

    except IOError as e:
        print(str(e))

    else:
        global HTTP_SERVER
        global HTTP_PORT
        global kafka_server
        global kafka_port
        global rootFullName
        global cert_dir
        global log_dir
        global lib_dir
        global client_bin_dir
        global server_bin_dir
        global MAX_MSG_SIZE
        global command_q_id
        global result_q_id
        global DB_host
        global DB_user
        global DB_pw
        global DB_dbName
        global  COMMAND_SEND
        global COMMAND_FIND
        global COMMAND_PRINT_ALL
        global COMMAND_SAVE_DB 
        global COMMAND_INIT_DB
        global COMMAND_LOAD_DB
        global COMMAND_START_PRECHECKER
        global COMMAND_END_PRECHECKER
        global COMMAND_START_TREESERVER
        global COMMAND_END_TREESERVER
        global COMMAND_START_CONSUMER
        global COMMAND_END_CONSUMER
        global COMMAND_LZ4_COMP
        global COMMAND_LZ4_DECOMP
        global COMMAND_AES_ENC
        global COMMAND_AES_DEC
        global default_AES
        global default_LZ4
        global policy_compress_ratio
        global NUMBER_OF_SEND_PROCESS
        global NUMBER_OF_LZ4_PROCESS
        global NUMBER_OF_AES_PROCESS
        global NUMBER_OF_PRECHECK_PROCESS
        global prechecker_sec_time_sleep
        global policy_similarity
        global max_block_num
        global policy_max_queue_size
        global PARTITION_SIZE
        global CHUNK_SIZE


        datas_result = json.load(open_json)
        open_json.close()


        HTTP_SERVER = datas_result['server_ip']
        HTTP_PORT = str(datas_result['http_port'])

        kafka_server = datas_result['server_ip']
        kafka_port = str(datas_result['kafka_port'])


        rootFullName = datas_result['rootFullName']

        cert_dir = datas_result['cert_dir']
        log_dir = datas_result['log_dir']
        lib_dir = datas_result['lib_dir']
        client_bin_dir = datas_result['client_bin_dir']
        server_bin_dir = datas_result['server_bin_dir']

        MAX_MSG_SIZE = datas_result['ipc_queue_max_msg_size']
        command_q_id = datas_result['ipc_command_queue_id']
        result_q_id = datas_result['ipc_result_queue_id']

        DB_host =  datas_result['DB_host']
        DB_user =  datas_result['DB_user']
        DB_pw =  datas_result['DB_pw']
        DB_dbName = datas_result['DB_dbName']




        COMMAND_SEND = datas_result['COMMAND_SEND']
        COMMAND_FIND = datas_result['COMMAND_FIND']
        COMMAND_PRINT_ALL = datas_result['COMMAND_PRINT_ALL']
        COMMAND_SAVE_DB = datas_result['COMMAND_SAVE_DB']
        COMMAND_INIT_DB = datas_result['COMMAND_INIT_DB']
        COMMAND_LOAD_DB = datas_result['COMMAND_LOAD_DB']

        COMMAND_START_PRECHECKER = datas_result['COMMAND_START_PRECHECKER']
        COMMAND_END_PRECHECKER = datas_result['COMMAND_END_PRECHECKER']
        COMMAND_START_TREESERVER = datas_result['COMMAND_START_TREESERVER']
        COMMAND_END_TREESERVER = datas_result['COMMAND_END_TREESERVER']
        COMMAND_START_CONSUMER = datas_result['COMMAND_START_CONSUMER']
        COMMAND_END_CONSUMER = datas_result['COMMAND_END_CONSUMER']

        COMMAND_LZ4_COMP = datas_result['COMMAND_LZ4_COMP']
        COMMAND_LZ4_DECOMP = datas_result['COMMAND_LZ4_DECOMP']
        COMMAND_AES_ENC = datas_result['COMMAND_AES_ENC']
        COMMAND_AES_DEC = datas_result['COMMAND_AES_DEC']


        default_AES = datas_result['POLICY_DEFAULT_AES']
        default_LZ4 = datas_result['POLICY_DEFAULT_LZ4']
        

        policy_compress_ratio = datas_result['POLICY_COMPRESS_RATIO']
        
        NUMBER_OF_SEND_PROCESS = datas_result['POLICY_NUMBER_OF_SEND_PROCESS']
        NUMBER_OF_LZ4_PROCESS = datas_result['POLICY_NUMBER_OF_LZ4_PROCESS']
        NUMBER_OF_AES_PROCESS = datas_result['POLICY_NUMBER_OF_AES_PROCESS']

        NUMBER_OF_PRECHECK_PROCESS = datas_result['POLICY_NUMBER_OF_PRECHECK_PROCESS']

        prechecker_sec_time_sleep = datas_result['POLICY_PRECHECKER_SEC_TIME_SLEEP']

        policy_similarity = datas_result['POLICY_SIMILARITY']

        max_block_num = datas_result['POLICY_MAX_BLOCK_NUM']

        policy_max_queue_size = datas_result['POLICY_MAX_QUEUE_SIZE']
        PARTITION_SIZE = datas_result['POLICY_PARTITION_SIZE']
        CHUNK_SIZE = datas_result['POLICY_CHUNK_SIZE']


loadConfigure()
