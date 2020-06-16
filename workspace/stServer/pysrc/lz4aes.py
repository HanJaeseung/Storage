import AESCipher
from configure import *
import ctypes
from ctypes import *
import os
import sys
import time

path, name = os.path.split(sys.argv[0])
if path == "":
    path ="."

compress_module = CDLL(path+"/../lib/lz4/liblz4.so.1.7.5")

def F_lz4(src):
    # compressed_data = lz4.frame.compress(src)
    # return compressed_data
    src_size = len(src)
    max_dst_size = compress_module.LZ4_compressBound(src_size)
    compressed_data = ctypes.create_string_buffer(max_dst_size)
    compressed_size = compress_module.LZ4_compress_default(src, compressed_data, src_size, max_dst_size)

    result = str(src_size) + "|H_LZ4_D|" + compressed_data.raw[0:compressed_size]
    return result

def F_d_lz4(filename, file_lock, text):
    print("*****Call LZ4 Compress*****")
    start = time.time()
    decompressed_data = "-1"
    try:
        src_size, header, compressed_data = text.partition("|H_LZ4_D|")

        src_size = int(src_size)        
        compressed_size = len(compressed_data)

        decompressed_data = ctypes.create_string_buffer(src_size)        
        decompressed_size = compress_module.LZ4_decompress_safe(compressed_data, decompressed_data, compressed_size, src_size)
        decompressed_data = decompressed_data.raw
        
    #decompressed_data = lz4.frame.decompress(text)


    except Exception as e:
        file_lock.acquire()
        f = open(log_dir+"/main_log", "a+")
        f.write("[ "+ filename + " ] lz4 Error\n" )
        f.write(str(e)+"\n")
        f.close()
        file_lock.release()
    sec = time.time() - start
    f = open("lz4_decomp_time.txt","a")
    f.write(str(sec) + "\n")
    f.close()
    return decompressed_data

def F_aes(str, AES_key):

    aes = AESCipher.AESCipher(AES_key)

    encrypt = aes.encrypt(str)

    return encrypt


def F_d_aes(filename, file_lock, text, AES_key):
    print("*****Call AES Decryption*****")
    decrypt = "-1"
    start = time.time()
    try:
        text = text.decode()
        aes = AESCipher.AESCipher(AES_key)

        decrypt = aes.decrypt(text)

    except Exception as e:
        file_lock.acquire()
        f = open(log_dir+'/main_log', 'a+')
        f.write("[ "+ filename + " ] aes Error\n" )
        f.write(str(e)+"\n")
        f.close()
        file_lock.release()

    sec = time.time() - start
    f =open("aes_dec_time.txt","a")
    f.write(str(sec) + "\n")
    f.close()
    return decrypt
