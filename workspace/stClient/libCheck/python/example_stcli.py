import sys
import stcli


def stcli_main(COMMAND):


    if COMMAND == "send":
       stcli.stcli_send()
        
    elif COMMAND == "find":
        stcli.stcli_find()

    elif COMMAND == "printAll":
       stcli.stcli_printAll()

    elif COMMAND == "saveDB":
        stcli.stcli_saveDB()

    elif COMMAND == "initDB":
        stcli.stcli_initDB()

    elif COMMAND == "loadDB":
        stcli.stcli_loadDB()

if __name__ == '__main__':
    COMMAND = sys.argv[1]
    stcli_main(COMMAND)

