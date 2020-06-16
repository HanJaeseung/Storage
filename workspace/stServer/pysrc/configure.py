import json

import os
import sys

path, name = os.path.split(sys.argv[0])
if path == "":
    path ="."

try:
    configure_fullname = path+"/../conf/server_configure"
    open_json = open(configure_fullname, 'r')
    print("Using config : "+ configure_fullname)


except IOError as e:
    print(str(e))

else:
    datas_result = json.load(open_json)
    open_json.close()


    ipc_key_queue_id = datas_result['ipc_key_queue_id']

    NUMBER_OF_RECV_PROCESS = None
    NUMBER_OF_AES_PROCESS = datas_result['POLICY_NUMBER_OF_AES_PROCESS']
    NUMBER_OF_LZ4_PROCESS = datas_result['POLICY_NUMBER_OF_LZ4_PROCESS']
    NUMBER_OF_WRITER_PROCESS = datas_result['POLICY_NUMBER_OF_WRITER_PROCESS']

    kafka_server = datas_result['server_ip']
    kafka_port = str(datas_result['kafka_port'])
    kafka_bootstrap_servers = kafka_server + ":" + kafka_port

    cert_dir = datas_result['cert_dir']
    log_dir = datas_result['log_dir']


    MAX_MSG_SIZE = datas_result['ipc_queue_max_msg_size']
    HTTP_SERVER = datas_result['server_ip']
    HTTP_PORT = datas_result['http_port']

    ipc_key_queue_id = datas_result['ipc_key_queue_id']

