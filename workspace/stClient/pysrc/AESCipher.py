# -*- coding: utf-8 -*-
import sys
import base64
import hashlib
from Crypto.Cipher import AES

BS = 16
pad = (lambda s: s + (BS -len(s) % BS) * chr(BS - len(s) % BS).encode())
unpad = (lambda s: s[:-ord(s[len(s)-1:])])

class AESCipher(object):
    def __init__(self, key):
       # self.key = key
        self.key = hashlib.sha256(key.encode()).digest()

    #    print("KEY : " + self.key)
      #  print("KEY LENGTH : " + str(len(self.key)))

    def encrypt(self, message):
       # if isinstance(message, str):
        #    message = message.encode('utf-8')
        raw = pad(message)
       # print(b"PADDING : " + raw)
        #print("PKCS #7 PADDING : " + str([l.encode('hex') for l in raw]))
        cipher = AES.new(self.key, AES.MODE_CBC, self.__iv())
        enc = cipher.encrypt(raw)
        return base64.b64encode(enc).decode()

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.__iv())
        dec = cipher.decrypt(enc)

        return unpad(dec)


    def __iv(self):
        return chr(0) * 16