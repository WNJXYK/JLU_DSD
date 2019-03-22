import socket, json
from multiprocessing import Process, Manager
from threading import Thread
import flask

# Global
manager = Manager()
socket_connection = manager.dict()
socket_server = None

room = manager.dict()

# Database
def database_init():
    # Virtual Init
    room["qwerty"] = "0001"
    room["popoqqq"] = "0001"
    # Init
    socket_connection["qwerty"] = None

def database_query_room(id): return room[id]

# Intelligence Controller

def report_data(id, type, data): print("%s(%s) : %s" % (type, id, data))

# Socket Service

def socket_init(ADDRESS):
    global socket_server
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind(ADDRESS)
    socket_server.listen(5)
    print("Socket Inited")

def socket_accept():
    global socket_server
    while True:
        client, _ = socket_server.accept()
        thread = Thread(target=socket_handle, args=(client, ))
        thread.setDaemon(True)
        thread.start()

def socket_handle(client):
    try:
        hello = json.loads(client.recv(1024))
        id, type, auth = hello["id"], hello["type"], hello["auth"]

        if auth != "Auth":
            client.send('{"status":-1, "msg":"Authenticate Failed."}'.encode("utf8"))
            client.close
            print("%s(%s) : Authenticate Failed" % (type, id))
            return

        # Receive Data
        if hello["socket"] == "in":
            print("%s(%s) : Reporter Online." % (type, id))
            client.send('{"status":0, "msg":"Hello Device."}'.encode("utf8"))
            while True:
                bytes = client.recv(1024)
                if len(bytes) == 0:
                    client.close()
                    print("%s(%s) : Offline"%(type, id))
                    return
                else:
                    report_data(id, type, str(bytes))


        # Register Sender
        if hello["socket"] == "out":
            if id not in socket_connection:
                client.send('{"status":-2, "msg":"Not Allowed Receiving."}'.encode("utf8"))
                print("%s(%s) : Not A Registered Device." % (type, id))
                client.close()
                return
            print("%s(%s) : Receiver Online." % (type, id))
            client.send('{"status":0, "msg":"Hello Device."}'.encode("utf8"))
            socket_connection[id] = client

    except: pass

def main():
    # Init Database
    database_init()

    # Init Server
    ADDRESS = ('127.0.0.1', 1033)
    socket_init(ADDRESS)
    server = Thread(target=socket_accept)
    server.setDaemon(True)
    server.start()


    while True:
        cmd = input()
        if cmd == "Exit":
            socket_server.close()
            exit()
        msg = input()
        if socket_connection[cmd] != None:
            socket_connection[cmd].send(('{"data":"%s"}'%msg).encode("utf8"))


if __name__ == '__main__': main()