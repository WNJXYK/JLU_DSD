import socket, json
from threading import Thread
from Demo.Database import Database


class Socket(object):
    def __init__(self, manager, hardware):
        self.socket_connection = manager.dict()
        self.socket_server = None
        self.hardware = hardware
        self.inQue = manager.Queue(100)
        self.outQue = manager.Queue(100)

    def run(self, Address = ('127.0.0.1', 1024)):
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 新建 Socket / Create a socket
        self.socket_server.bind(Address)
        self.socket_server.listen(5)

        thread = Thread(target=self.accept)  # 监听线程 / Listening thread
        thread.setDaemon(True)
        thread.start()

        thread = Thread(target=self.send_thread)  # 监听指令队列线程 / Listening command queue thread
        thread.setDaemon(True)
        thread.start()

        print("Socket is running on %s:%d" % Address)

    def send_thread(self):
        while True:
            (hid, msg) = self.outQue.get(True)
            try:
                self.socket_connection[hid].send(msg.encode("utf8"))
            except: pass

    def accept(self):
        while True:
            client, _ = self.socket_server.accept()
            thread = Thread(target=self.handle, args=(client,))
            thread.setDaemon(True)
            thread.start()

    def handle(self, client):
        try:
            hello = json.loads(client.recv(1024))
            id, type, auth = hello["id"], hello["type"], hello["auth"]

            # Authenticate Key
            if auth != "Auth":
                client.send('{"status":-1, "msg":"Authenticate Failed."}'.encode("utf8"))
                client.close
                print("%s(%s) : Authenticate Failed" % (type, id))
                return

            # Authenticate Hardware
            if not Database.is_hardware(id):
                client.send('{"status":-3, "msg":"Not An Registered Hardware."}'.encode("utf8"))
                print("%s(%s) : Not A Registered Hardware." % (type, id))
                client.close()
                return

            # Receive Data
            if hello["socket"] == "in":
                self.hardware.online(id, type)
                print("%s(%s) : Reporter Online." % (type, id))
                client.send('{"status":0, "msg":"Hello Device."}'.encode("utf8"))
                while True:
                    bytes = client.recv(1024)
                    if len(bytes) == 0:
                        client.close()
                        self.hardware.offline(id)
                        print("%s(%s) : Offline"%(type, id))
                        return
                    else:
                        self.hardware.report(id, bytes)
                        self.inQue.put(id)


            # Register Sender
            if hello["socket"] == "out":
                # Authenticate Device
                if not Database.is_device(id):
                    client.send('{"status":-2, "msg":"Not An Registered Device."}'.encode("utf8"))
                    print("%s(%s) : Not A Registered Device." % (type, id))
                    client.close()
                    return
                print("%s(%s) : Receiver Online." % (type, id))
                client.send('{"status":0, "msg":"Hello Device."}'.encode("utf8"))
                self.socket_connection[id] = client

        except: pass
