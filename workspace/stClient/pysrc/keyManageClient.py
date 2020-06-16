
import bs4
import requests
from Crypto.PublicKey import RSA
import sys
import os
import binascii
import hashlib
from configure import *


CERT_FILE = "storage.crt"
KEY_FILE = "public.key"
P7B_FILE = "storage.p7b"

#AES_key = binascii.hexlify(os.urandom(32))[:32]

AES_key = binascii.hexlify(os.urandom(100))[:100]

#AES_key = hashlib.sha256(key.encode()).digest()
#AES_key = binascii.hexlify(os.urandom(32))[:32]
#print(len(AES_key))
#AES_key = "513fe58393f100b0c904434f3470e7ed"
# AES_key = os.urandom(32)
# AES_key = sys.argv[1]
# print(AES_key)


def rsa_encrypt(msg, public_key_string):
    public_key = RSA.importKey(public_key_string)

    encdata = public_key.encrypt(msg, 32)
    # print("---------------2. AES Key Msg Encryption used RSA Public Key--------------")
    # print(encdata)
    # print
  
    return encdata



def http_get_rsa_public_key():
            print(HTTP_SERVER) 
            r = requests.get("http://"+HTTP_SERVER+":"+str(HTTP_PORT))

            version = r.raw.version
            if version == 10 :
              changed_version = "HTTP/1.0"
            elif version == 11:
              changed_version = "HTTP/1.1"

#            print
#            print("--------------------------1. get RSA Public Key-------------------------")
#            print(changed_version + " " + str(r.status_code) +" "+str(r.reason))
#            print("Server : " + r.headers['Server'])
#            print("Date : " + r.headers['Date'])
#            print("Content-Type : " + r.headers['Content-type'])
            
#            print(r.content)       


            html = bs4.BeautifulSoup(r.text, "html.parser")

            pkcs7_buf = html.body.pkcs7.get_text()

            cwd = os.getcwd().split('/')[-1]
            print("------------------------")
            #print(cert_dir)
            cert_dir_path = ""
            if cwd == "c" :
               cert_dir_path = "../" + cert_dir
            else :
               cert_dir_path = cert_dir
            print("======================")
            #print(cert_dir_path)
            print(pkcs7_buf)
            open(os.path.join(cert_dir_path, P7B_FILE), "wb").write(pkcs7_buf)
            os.system("openssl pkcs7 -print_certs -in " + os.path.join(cert_dir_path, P7B_FILE) + " -out " + os.path.join(cert_dir_path,CERT_FILE))
            os.system("openssl x509 -pubkey -noout -in " + os.path.join(cert_dir_path,CERT_FILE) + " > " + os.path.join(cert_dir_path,KEY_FILE))

            f = open(os.path.join(cert_dir_path,KEY_FILE), 'r')
            public_key_string = f.read()
            f.close()
          #  public_key_string = html.body.public_key.get_text()

            return public_key_string

def http_post_aes_private_key(enc_AES_key):
            params = {'AES_key' : enc_AES_key}

            r = requests.post(url="http://"+HTTP_SERVER+":"+str(HTTP_PORT), data=params)

            version = r.raw.version
            if version == 10 :
              changed_version = "HTTP/1.0"
            elif version == 11:
              changed_version = "HTTP/1.1"

#            print("--------------------3. post  Encrypted AES Key Message--------------------")
#            print(changed_version + " " + str(r.status_code) +" "+str(r.reason))
#            print("Server : " + r.headers['Server'])
#            print("Date : " + r.headers['Date'])
#            print("Content-Type : " + r.headers['Content-type'])
#            print(r.content)   
#            print("-------------------------------------------------------------------------")




# if __name__=='__main__':

#     public_key_string = http_get_rsa_public_key()   
#     enc_AES_key =  rsa_encrypt(AES_key, public_key_string)
#     http_post_aes_private_key(enc_AES_key[0])


