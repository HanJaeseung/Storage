#include <Python.h>


int main(int argc, char * argv[])
{

    char* command = malloc(sizeof(char) * 100);


    char* compressed_data;
    int comp_size;

    char* enc_data;

    char* public_rsa_key;
    PyObject* rsa_enc_data;    

    PyObject* tree;



    while(1)
    {
        printf("command : ");
        scanf("%s", command);

        // 압축 요청
        if (!strcmp(command, "comp"))
        {   
            char* src = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz";
            int src_size = strlen(src);

            compressed_data = NULL;
            comp_size = 0;

            printf("[SRC DATA]");
            printf("%s\n\n",src);
            Kms_Req_ComPress_Lz4(&compressed_data, &comp_size, src, src_size);

            printf("[COMP DATA]");
            printf("%s\n\n", compressed_data);

             // You Need "free"
            //free(compressed_data);
        }

        // 압축 해제 요청
        else if (!strcmp(command, "decomp"))
        {      
            
            char* decompressed_data = NULL;
            int decomp_size = 0;

            printf("[SRC DATA]");
            printf("%s\n\n",compressed_data);

            Kms_Req_DeComPress_Lz4(&decompressed_data, &decomp_size, compressed_data, comp_size);

            printf("[DECOMP DATA]");
            printf("%s\n\n", decompressed_data);

            // You Need "free"
            //free(decompressed_data);

        }

        // 암호화 요청
        else if (!strcmp(command, "enc"))
        {      

            char* src = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz";
            printf("Org data : %s\n\n", src);

            int src_size = strlen(src);
            int enc_size = 0;

            char* AES_key = "Hello World";

            Kms_Req_Encryption_AES(&enc_data, &enc_size, src, src_size, AES_key);

            printf("Enc data : %s\n", enc_data);
        }

        // 복호화 요청
        else if (!strcmp(command, "dec"))
        {      
            char* dec_data;
            int enc_size = strlen(enc_data);
            int dec_size = 0;

            printf("Enc data : %s\n\n", enc_data);

            char* AES_key = "Hello World";

            Kms_Req_Decryption_AES(&dec_data, &dec_size, enc_data, enc_size, AES_key);
            printf("Dec data : %s\n", dec_data);
        }

        // RSA Public Key 요청
        else if (!strcmp(command, "httpget"))
        {      

            public_rsa_key = NULL;
            Kms_Http_Get_Rsa_Public_Key(&public_rsa_key);


            printf("%s\n", public_rsa_key);
        }

        // RSA로 AES Key 암호화
        else if (!strcmp(command, "rsa"))
        {      
            rsa_enc_data = NULL;
            char* aes_key = "Hello World";
            Kms_Rsa_Encrypt(&rsa_enc_data, aes_key, public_rsa_key);

            Py_Initialize();
            PyObject_Print(rsa_enc_data, stdout, Py_PRINT_RAW);
            Py_Finalize();

            printf("\n");
        }

        // RSA로 암호화 된 AES Key 전달
        else if (!strcmp(command, "httppost"))
        {      
            Kms_Http_Post_Aes_Private_Key(rsa_enc_data);
            printf("Sended RSA Encrpyted AES Key!\n");
        }

        // TreeServer의 Tree 정보 요청
        else if (!strcmp(command, "getTree"))
        {      
            Kms_Req_getTree(&tree);
        }

        // TreeServer에 Tree정보 전달
        else if (!strcmp(command, "setTree"))
        {      
            Kms_Req_setTree(tree);
        }

        // TreeServer에 모든 Tree정보 전달
        else if (!strcmp(command, "setTreeAll"))
        {      
            Kms_Req_setTreeAll(tree);
        }

        // TreeServer에 있는 정보 DB에 저장
        else if (!strcmp(command, "saveDB"))
        {
            Kms_Req_saveDB();
        }

        // DB에 있는 정보 TreeServer에 load
        else if (!strcmp(command, "loadDB"))
        {
            Kms_Req_loadDB();
        }

        // DB 정보 초기화
        else if (!strcmp(command, "initDB"))
        {
            Kms_Req_initDB();
        }
        // 데이터 전송 - 내부적으로 getTree, setTree, compare, lz4, aes 모두 포함됨
        else if (!strcmp(command, "send"))
        {
            Kms_Req_Send();
        }
        
        else if (!strcmp(command, "startPC"))
        {
            Kms_Start_Prechecker();
        }

        else if (!strcmp(command, "endPC"))
        {
            Kms_End_Prechecker();
        }

        else if (!strcmp(command, "startTS"))
        {
            Kms_Start_TreeServer();
        }

        else if (!strcmp(command, "endTS"))
        {
            Kms_End_TreeServer();
        }

        else if (!strcmp(command, "startCS"))
        {
            Kms_Start_Consumer();
        }

        else if (!strcmp(command, "endCS"))
        {
            Kms_End_Consumer();
        }

        else if(!strcmp(command, "test"))
        {

            char* src = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz";
            int src_size = strlen(src);

            compressed_data = NULL;
            comp_size = 0;
            
            enc_data = NULL;
            int enc_size = 0;

            char* dec_data = NULL;
            int dec_size = 0;

            char* decompressed_data = NULL;
            int decomp_size = 0;

    

            char* AES_key = "Hello World";


            Kms_Req_ComPress_Lz4(&compressed_data, &comp_size, src, src_size);
            printf("Comp : %s\n\n", compressed_data);
           
            Kms_Req_Encryption_AES(&enc_data, &enc_size, compressed_data, comp_size, AES_key);
            printf("Enc : %s\n\n", enc_data);

            Kms_Req_Decryption_AES(&dec_data, &dec_size, enc_data, enc_size, AES_key);
            printf("Dec : %s\n\n", dec_data);

            Kms_Req_DeComPress_Lz4(&decompressed_data, &decomp_size, dec_data, dec_size);
            printf("Decomp : %s\n\n", decompressed_data);



            
        }
        else if (!strcmp(command, "clear"))
        {
            system("clear");
            
        }
        else
        {
            printf("Error !! Invalid Command.. \n");

        }

    }
    free(tree);
    
    

    return 0;
} 

