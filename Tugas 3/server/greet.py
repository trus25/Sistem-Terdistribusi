import shlex
import os
import time
import Pyro4
import Pyro4.errors
import json
import threading


class Server(object):
    def __init__(self):
        self.connected_device = []
        self.connected_device_thread_job = []

    @Pyro4.expose
    def connected_device_list(self) -> str:
        return 'connected device : ' + ', '.join(self.connected_device)

    @Pyro4.expose
    def connected_device_ls(self) -> str:
        return ','.join(self.connected_device)

    @Pyro4.expose
    def help(self) -> str:
        return "1. list: list -a or list -all\n" \
               "2. create: create namefile1 namefile2 namefile3 ...\n" \
               "3. read: read namefile\n" \
               "4. delete: deleete namefile1 namefile2 namefile3 ...\n" \
               "5. create: create namefile1 namefile2 namefile3 ...\n" \
               "6. exit: to exit"

    @Pyro4.expose
    def connected_device_add(self, id):
        print('register ' + id)
        self.connected_device.append(id)

    @Pyro4.expose
    def connected_device_delete(self, id):
        print('unregister ' + id)
        self.connected_device.remove(id)

    @Pyro4.expose
    def command_not_found(self) -> str:
        return "command not found"

    @Pyro4.expose
    def command_success(self) -> str:
        return "operation success"

    @Pyro4.expose
    def bye(self) -> str:
        return "bye!"

    @Pyro4.expose
    def ok(self) -> str:
        return "ok"

    @Pyro4.expose
    def fail(self) -> str:
        return "fail"

    @Pyro4.expose
    def ping_interval(self) -> int:
        return 3

    @Pyro4.expose
    def max_retries(self) -> int:
        return 2

    @Pyro4.expose
    def new_thread_job(self, id) -> str:
        t = threading.Thread(target=self.__new_thread_job, args=(id,))
        t.start()
        self.connected_device_thread_job.append(t)
        return self.ok()

    def __connect_heartbeat_server(self, id):
        time.sleep(self.ping_interval())
        try:
            uri = "PYRONAME:heartbeat-{}@localhost:7777".format(id)
            server = Pyro4.Proxy(uri)
        except:
            return None
        return server

    def __new_thread_job(self, id):
        server = self.__connect_heartbeat_server(id)
        while True:
            try:
                res = server.signal_heartbeat()
                print(res)
            except (Pyro4.errors.ConnectionClosedError, Pyro4.errors.CommunicationError) as e:
                print(str(e))
                break
            time.sleep(self.ping_interval())

    def __delete_file(self, path, name) -> str:
        res = self.command_success()
        try:
            os.remove(os.path.join(path, name))
        except Exception as e:
            return str(e)
        return res

    def __process_file(self, path, name, operation, *args, **kwargs) -> str:
        res = self.command_success()
        try:
            f = open(os.path.join(path, name), operation)
            if operation == "r":
                res = f.read()
            elif operation == "a+":
                f.write(kwargs.get('content', None))
            f.close()
        except Exception as e:
            return str(e)
        return res

    def __root_folder_exists(self, root):
        if not os.path.exists(root):
            os.makedirs(root)

    def __get_storage_path(self) -> str:
        root = os.path.dirname(os.path.abspath(__file__)) + "/storage"
        self.__root_folder_exists(root)
        return root

    @Pyro4.expose
    def list(self, req) -> str:
        args = req.split()
        dirs = os.listdir(self.__get_storage_path())
        status = ""
        if len(args) == 1:
            for dir in dirs:
                status = status + "{}   ".format(dir)
        elif len(args) == 2 and args[1] in ["-a", "-all"]:
            status = status + "."
            for dir in dirs:
                status = status + "\n{}".format(dir)
        else:
            status = "command failed, use -a/-all on the second argument"
        return status

    @Pyro4.expose
    def create(self, req) -> str:
        args = shlex.split(req)
        dirs = self.__get_storage_path()
        status = ""
        if len(args) > 1:
            for file_name in args[1:]:
                status = self._process_file(dirs, file_name, "w+")
                if status != self.command_success():
                    return status
        else:
            status = "command failed, should be namefile on the second argument and so on"
        return status

    @Pyro4.expose
    def delete(self, req) -> str:
        args = shlex.split(req)
        dirs = self.__get_storage_path()
        status = ""
        if len(args) > 1:
            for file_name in args[1:]:
                status = self.delete_file(dirs, file_name)
                if status != self.command_success():
                    return status
        else:
            status = "command failed, should be namefile on the second argument and so on"
        return status

    @Pyro4.expose
    def read(self, req) -> str:
        args = shlex.split(req)
        dirs = self.__get_storage_path()
        status = ""
        if len(args) > 1:
            status = self._process_file(dirs, args[1], "r")
        else:
            status = "command failed, should be namefile on the second argument and so on"
        return status

    @Pyro4.expose
    def update(self, req):
        args = shlex.split(req)
        dirs = self.__get_storage_path()
        status = ""
        if len(args) == 4:
            if args[1] in ["-append", "-a"]:
                status = self._process_file(dirs, args[2], "a+", content=args[3])
            elif args[1] in ["-overwrite", "-o"]:
                status = self._process_file(dirs, args[2], "w")
                status = self._process_file(dirs, args[2], "a+", content=args[3])
            else:
                status = "command gagal, gunakan opsi -append / -a, -overwrite / -o\ncontoh: update --append text.txt 'lorem ipsumsit dolor amet'"
        else:
            status = "command gagal, gunakan opsi -append / -a, -overwrite / -o\ncontoh: update --append text.txt 'lorem ipsumsit dolor amet'"
        return status

    @Pyro4.expose
    def down_my_server(self) -> str:
        time.sleep(self.ping_interval() + 1)
        return self.ok()