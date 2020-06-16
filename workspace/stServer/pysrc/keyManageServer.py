# -*- coding: utf-8 -*-
import os
import BaseHTTPServer
from urlparse import parse_qs
from OpenSSL import crypto
from Crypto.PublicKey import RSA
import time
import cgi
import sysv_ipc
import json
from configure import *


AES_key = None

CERT_FILE = "storage.crt"
KEY_FILE = "private.key"
P7B_FILE = "storage.p7b"

#cert_dir = "/root/Storage/V\&V/stServer/cert"

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):


    def readPrivateKey(self):
        h = open(os.path.join(cert_dir, KEY_FILE), 'r')
        key = RSA.importKey(h.read()) # private key read
        h.close()
        return key

    def readP7B(self):
        f = open(os.path.join(cert_dir, P7B_FILE), 'r')
        pkcs7_buf = f.read()
        f.close()

        return pkcs7_buf

    def rsa_decrypt(self, msg):
        private_key = self.readPrivateKey()
        decdata = private_key.decrypt(msg)
        print

        print("[GET AES KEY] "+ decdata)
        return decdata


    def query_get(self, queryData, key, default=""):
        """Helper for getting values from a pre-parsed query string"""
        return queryData.get(key, [default])[0]

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        createPEM()

        print
        # Extract values from the query string
        path, _, query_string = self.path.partition('?')
        query = parse_qs(query_string)

        response = None

       # print(u"[START]: Received GET for %s with query: %s" % (path, query))

        #if self.path.endswith('request_rsa_public_key'):
        #if path == "/request_rsa_public_key":

        """Respond to a GET request."""

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>RSA Public Key </title></head>\n")

        # private_key = self.readPEM()
        # public_key = private_key.publickey()
        # public_key_string = public_key.exportKey()

        pkcs7_buf = self.readP7B()

        self.wfile.write("<body><pkcs7>"+ str(pkcs7_buf)+"</pkcs7>\n")

        self.wfile.write("</body></html>\n")

    def do_POST(self):
        print
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        # Begin the response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
        self.wfile.write('Path: %s\n' % self.path)
        self.wfile.write('Form data:\n')

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                del file_data
                self.wfile.write('\tUploaded %s as "%s" (%d bytes)\n' % \
                        (field, field_item.filename, file_len))
            else:
                # Regular form value
                self.wfile.write('\t%s=%s\n' % (field, form[field].value))

        AES_key = self.rsa_decrypt(form[field].value)
    
        try:
            key_mq = sysv_ipc.MessageQueue(ipc_key_queue_id, max_message_size=MAX_MSG_SIZE)
            key_mq.send(AES_key)
        except Exception as e:
            print(e , "ERR MQ !")

        print

        return

       

def createPEM():
    # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "KR"
        cert.get_subject().ST = "A"
        cert.get_subject().L = "B"
        cert.get_subject().O = "C"
        cert.get_subject().OU = "KETI"
        cert.get_subject().CN = "D"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha1')

        open(os.path.join(cert_dir, CERT_FILE), "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        open(os.path.join(cert_dir, KEY_FILE), "wb").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

        
        os.system("openssl crl2pkcs7 -nocrl -certfile "+os.path.join(cert_dir, CERT_FILE)+" -out "+os.path.join(cert_dir, P7B_FILE))
        print("[CREATE] RSA Key")


def HTTP_Server_main():

#    createPEM()

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HTTP_SERVER, HTTP_PORT), MyHandler)

    print "[SERVER START] ", time.asctime(), "Server Starts - %s:%s" % (HTTP_SERVER, HTTP_PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print "[SERVER END] ", time.asctime(), "Server Stops - %s:%s" % (HTTP_SERVER, HTTP_PORT)


#if __name__=='__main__':
#    main()

