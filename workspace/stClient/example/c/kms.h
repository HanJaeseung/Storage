#include <Python.h>

void Kms_Req_ComPress_Lz4(char** compressed_data, int* compressed_size, char* src, int src_size);
void Kms_Req_DeComPress_Lz4(char** decompressed_data, int* decompressed_size, char* src, int src_size);

void Kms_Req_Encryption_AES(char** enc_data, int* enc_size, char* src, int src_size, char* AES_key);
void Kms_Req_Decryption_AES(char** dec_data, int* dec_size, char* src, int src_size, char* AES_key);

void Kms_Http_Get_Rsa_Public_Key(char** public_rsa_key);
void Kms_Rsa_Encrypt(PyObject** enc_data, char* msg, char* public_rsa_key);
void Kms_Http_Post_Aes_Private_Key(PyObject* enc_data);

void Kms_Req_getTree(PyObject** tree);

void Kms_Req_setTree(PyObject* tree);
void Kms_Req_setTreeAll(PyObject* tree);

void Kms_Req_saveDB();
void Kms_Req_initDB();
void Kms_Req_loadDB();

void Kms_Req_Send();


void Kms_Start_Prechecker();
void Kms_End_Prechecker();

void Kms_Start_TreeServer();
void Kms_End_TreeServer();

void Kms_Start_Consumer();
void Kms_End_Consumer();

