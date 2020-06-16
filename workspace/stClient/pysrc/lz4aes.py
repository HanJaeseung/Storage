
import AESCipher
from configure import *
import configure
import ctypes
from ctypes import *
import os
import sys
import time
import datetime


#try:
#     path, name = os.path.split(sys.argv[0])
#     if path == "":
#         path ="."

#     compress_module = CDLL(path+"/../lib/lz4/liblz4.so.1.7.5")

#except:
#     compress_module = CDLL("../lib/lz4/liblz4.so.1.7.5")

compress_module =  CDLL(lib_dir + "/lz4/liblz4.so.1.7.5")

def F_lz4(src):
    #print("*****Call LZ4 Compress*****")

    #start = time.time()
    # compressed_data = lz4.frame.compress(src)
    # return compressed_data
    src_size = len(src)
    max_dst_size = compress_module.LZ4_compressBound(src_size)
    compressed_data = ctypes.create_string_buffer(max_dst_size)
    compressed_size = compress_module.LZ4_compress_default(src, compressed_data, src_size, max_dst_size)

    result = str(src_size) + "|H_LZ4_D|" + compressed_data.raw[0:compressed_size]

    #sec = time.time() - start
    #times = str(datetime.timedelta(seconds=sec)).split(".")
    #times = times[0]
    #f = open("lz4_time.txt", "a")
    #f.write(str(sec) + "\n")
    #f.close()
    return result

def F_d_lz4(src):
    #decompressed_data = lz4.frame.decompress(src)
    #return decompressed_data

    src_size, compressed_data = src.split("|H_LZ4_D|")
    src_size = int(src_size)

    compressed_size = len(compressed_data)
    decompressed_data = ctypes.create_string_buffer(src_size)
    decompressed_size = compress_module.LZ4_decompress_safe(compressed_data, decompressed_data, compressed_size, src_size)
    decompressed_data = decompressed_data.raw
    return decompressed_data

def F_aes(inputstr, AES_key):
    #print("*****Call AES Encrytion*****")
    #start = time.time()
    aes = AESCipher.AESCipher(AES_key)

    encrypt = aes.encrypt(inputstr)
    #sec = time.time() - start
    #times = str(datetime.timedelta(seconds=sec)).split(".")
    #times = times[0]
    #f = open("aes_time.txt", 'a')
    #f.write(str(sec) + "\n")
    #f.close()

    return encrypt


def F_d_aes(str, AES_key):
    str = str.decode()
    aes = AESCipher.AESCipher(AES_key)

    
    decrypt = aes.decrypt(str)

    return decrypt


def cinterface_producer_F_lz4(data):
    compressed_data = F_lz4(data)
    return [compressed_data, len(compressed_data)]


def cinterface_producer_F_d_lz4(data):
    
    decompressed_data = F_d_lz4(data)

    return [decompressed_data, len(decompressed_data)]


def cinterface_producer_F_aes(str, AES_key):
    encrypt = F_aes(str, AES_key)

    return [encrypt, len(encrypt)]


def cinterface_producer_F_d_aes(str, AES_key):
    
    decrypt =F_d_aes(str, AES_key)

    return [decrypt, len(decrypt)]
