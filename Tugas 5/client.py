import Pyro4
import base64
import json
import sys

namainstance = sys.argv[1]

def get_fileserver_object():
    uri = "PYRONAME:{}@localhost:7777" . format(namainstance)
    fserver = Pyro4.Proxy(uri)
    fserver.setName(namainstance)
    fserver.setPyroObject()
    return fserver

def manageCommand(cmd):
    listCommand = ['list', 'create', 'read', 'update', 'delete', 'help']
    cmdArr = cmd.split(' ')

    if cmdArr[0] == 'exit':
        return ['exit', 'Program closed']
    if cmdArr[0] in listCommand:
        return cmdArr
    elif cmdArr[0] not in listCommand:
        return ['error', 'Command unknown']
    else:
        return None

if __name__=='__main__':
    proxy = get_fileserver_object()
    print("type 'help' to see all the command")
    while True:
        cmd = input("command: ")
        cmd = manageCommand(cmd)
        if cmd[0] == 'create':
            print(proxy.create(cmd[1],namainstance))
        elif cmd[0] == 'read':
            print(proxy.read(cmd[1]))
        elif cmd[0] == 'update':
            print(proxy.update(cmd[1],cmd[2],namainstance))
        elif cmd[0] == 'delete':
            print(proxy.delete(cmd[1],namainstance))
        elif cmd[0] == 'list':
            print(proxy.list())
        elif cmd[0] == 'help':
            print("List of commands : ")
            print("1. create [filename]")
            print("2. read [filename]")
            print("3. update [filename]")
            print("4. delete [filename]")
            print("5. list")
            print("6. help")
            print("7. exit")
        elif cmd[0] == 'error':
            print(cmd[1])
        elif cmd[0] == 'exit':
            print(cmd[1])
            exit()