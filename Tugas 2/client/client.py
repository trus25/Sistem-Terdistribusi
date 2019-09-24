import Pyro4
import subprocess



def get_server():

    #ganti "localhost dengan ip yang akan anda gunakan sebagai server"

    uri = "PYRONAME:greetserver@localhost:7777"

    gserver = Pyro4.Proxy(uri)

    return gserver



if __name__=='__main__':

    server = get_server()

    if server == None:

        exit()

    check = True
    print("Hello, use 'help' to see all commands")
    while check:

        arg = input ("-> ").lower()
        args = arg.split()
        if args[0] == 'help':
            print(server.help())
        elif args[0] == 'list':
            print(server.list(arg))
        elif args[0] == 'create':
            print(server.create(arg))
        elif args[0] == 'delete':
            print(server.delete(arg))
        elif args[0] == 'read':
            print(server.read(arg))
        elif args[0] == 'update':
            print(server.update(arg))
        elif args[0] == 'exit':
            print(server.bye())
            check = False
        else:
            print(server.command_fail())
