#include "kms.h"

void Kms_Req_ComPress_Lz4(char** compressed_data, int* compressed_size, char* src, int src_size)
{
    Py_Initialize();
    
    PyObject* myModuleString = PyString_FromString((char*) "lz4aes");
    PyObject* myModule = PyImport_Import(myModuleString);
   

    if (myModule == NULL) {
        printf("Error import module\n");
        PyErr_Print();
        exit(-1);
    }

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"cinterface_producer_F_lz4");

    if (myFunction == NULL) {
        PyErr_Print();
        printf("Error getting attribute\n");
        exit(-1);

    }


    PyObject* pyo_src = PyString_FromStringAndSize(src, src_size);
    
    if (pyo_src == NULL) {
        PyErr_Print();
        printf("Error 3\n");
        exit(-1);

    } 



    PyObject* args = PyTuple_Pack(1, pyo_src);
    

    if (args == NULL) {
        PyErr_Print();
        printf("Error 4\n");
        exit(-1);

    }

    PyObject* ret = PyObject_CallObject(myFunction, args);

    if (ret == NULL) {
        PyErr_Print();
        printf("Error 5\n");
        exit(-1);

    }

    PyObject* pyo_comp_data = PyList_GetItem(ret, 0);

    if (pyo_comp_data == NULL) {
        PyErr_Print();
        printf("Error 5\n");
        exit(-1);

    }
    

    PyObject* pyo_comp_size  = PyList_GetItem(ret, 1);

    *compressed_size = (int)PyLong_AsLong(pyo_comp_size);
    //Py_ssize_t comp_size = PyLong_AsSsize_t(pyo_comp_size);
    //Py_ssize_t *p = comp_size;

    //PyObject_Print(pyo_comp_data,stdout,0);
    //PyObject_Print(pyo_comp_size,stdout,0);
    //printf("%d\n\n", *compressed_size);
    
    int a = PyString_AsStringAndSize (pyo_comp_data, compressed_data, pyo_comp_size);
  
    //printf("%s\n", *test);
    //printf("%s\n", test);


    Py_Finalize();
}



void Kms_Req_DeComPress_Lz4(char** decompressed_data, int* decompressed_size, char* src, int src_size)
{
    Py_Initialize();
 
    PyObject* myModuleString = PyString_FromString((char*) "lz4aes");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"cinterface_producer_F_d_lz4");

    PyObject* pyo_src = PyString_FromStringAndSize(src, src_size);

    PyObject* args = PyTuple_Pack(1, pyo_src);


    PyObject* ret = PyObject_CallObject(myFunction, args);

    PyObject* pyo_decomp_data = PyList_GetItem(ret, 0);
    PyObject* pyo_decomp_size  = PyList_GetItem(ret, 1);

    *decompressed_size = (int)PyLong_AsLong(pyo_decomp_size);

    PyString_AsStringAndSize (pyo_decomp_data, decompressed_data, pyo_decomp_size);


    Py_Finalize();

}

void Kms_Req_Encryption_AES(char** enc_data, int* enc_size, char* src, int src_size, char* AES_key)
{
    Py_Initialize();
 
    PyObject* myModuleString = PyString_FromString((char*) "lz4aes");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"cinterface_producer_F_aes");

    PyObject* pyo_src = PyString_FromStringAndSize (src, src_size);
    PyObject* pyo_key = PyString_FromString(AES_key);

    PyObject* args = PyTuple_Pack(2, pyo_src, pyo_key);

    PyObject* ret = PyObject_CallObject(myFunction, args);

    PyObject* pyo_enc_data = PyList_GetItem(ret, 0);
    PyObject* pyo_enc_size  = PyList_GetItem(ret, 1);

    *enc_size = (int)PyLong_AsLong(pyo_enc_size);

    int a = PyString_AsStringAndSize (pyo_enc_data, enc_data, pyo_enc_size);

    printf("%d\n",a);

    Py_Finalize();
}

void Kms_Req_Decryption_AES(char** dec_data, int* dec_size, char* src, int src_size, char* AES_key)
{
    Py_Initialize();

 
    PyObject* myModuleString = PyString_FromString((char*) "lz4aes");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"cinterface_producer_F_d_aes");

    PyObject* pyo_src = PyString_FromStringAndSize (src, src_size);
    PyObject* pyo_key = PyString_FromString(AES_key);

    PyObject* args = PyTuple_Pack(2, pyo_src, pyo_key);

    PyObject* ret = PyObject_CallObject(myFunction, args);

    PyObject* pyo_dec_data = PyList_GetItem(ret, 0);
    PyObject* pyo_dec_size  = PyList_GetItem(ret, 1);

    *dec_size = (int)PyLong_AsLong(pyo_dec_size);


    PyString_AsStringAndSize (pyo_dec_data, dec_data, pyo_dec_size);


    Py_Finalize();
}


void Kms_Http_Get_Rsa_Public_Key(char** public_rsa_key)
{
    Py_Initialize();
    PyObject* myModuleString = PyString_FromString((char*) "keyManageClient");
    
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"http_get_rsa_public_key");

    PyObject* args = PyTuple_Pack(0);

    PyObject* ret = PyObject_CallObject(myFunction, args);

    *public_rsa_key = PyString_AsString(ret);

    Py_Finalize();
}



void Kms_Rsa_Encrypt(PyObject** enc_data, char* msg, char* public_rsa_key)
{
    Py_Initialize();
 
    PyObject* myModuleString = PyString_FromString((char*) "keyManageClient");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"rsa_encrypt");

    PyObject* pyoMsg = PyString_FromString(msg);
    PyObject* pyo_public_rsa_key = PyString_FromString(public_rsa_key);
    PyObject* args = PyTuple_Pack(2, pyoMsg, pyo_public_rsa_key);

    *enc_data = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}
void Kms_Http_Post_Aes_Private_Key(PyObject* enc_data)
{
    Py_Initialize();
 
    PyObject* myModuleString = PyString_FromString((char*) "keyManageClient");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"http_post_aes_private_key");
    PyObject* args = PyTuple_Pack(1, enc_data);

    PyObject* ret = PyObject_CallObject(myFunction, args);


    Py_Finalize();
}
void Kms_Req_getTree(PyObject** tree)
{
    Py_Initialize();
 
    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_getTree");
    PyObject* args = PyTuple_Pack(0);

    *tree = PyObject_CallObject(myFunction, args);


    Py_Finalize();

}

void Kms_Req_setTree(PyObject* tree)
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_setTree");
    PyObject* args = PyTuple_Pack(1, tree);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}

void Kms_Req_setTreeAll(PyObject* tree)
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_setTreeAll");
    PyObject* args = PyTuple_Pack(1, tree);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}
void Kms_Req_saveDB()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_saveDB");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}

void Kms_Req_initDB()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_initDB");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}

void Kms_Req_loadDB()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_loadDB");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}
void Kms_Req_Send()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_send");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}

void Kms_Start_Prechecker()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_Start_Prechecker");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}
void Kms_End_Prechecker()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_End_Prechecker");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}

void Kms_Start_TreeServer()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_Start_TreeServer");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}
void Kms_End_TreeServer()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_End_TreeServer");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}
void Kms_Start_Consumer()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_Start_Consumer");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}
void Kms_End_Consumer()
{
    Py_Initialize();

    PyObject* myModuleString = PyString_FromString((char*) "stcli");
    PyObject* myModule = PyImport_Import(myModuleString);

    PyObject* myFunction = PyObject_GetAttrString(myModule,(char*)"stcli_End_Consumer");
    PyObject* args = PyTuple_Pack(0);

    PyObject* myResult = PyObject_CallObject(myFunction, args);

    Py_Finalize();
}
