import socket, json
from multiprocessing import Manager
from threading import Thread
from flask import Flask, request, json, jsonify
from flask_cors import *


from Demo.Database import Database
from Demo.Controller.Controller import Controller
from Demo.Server.Hardware import Hardware
from Demo.Server.IController import IController


# Global
manager = Manager()
socket_connection = manager.dict()
socket_server = None

hardware = Hardware(manager)
controller = Controller()
iController = IController(hardware, controller, socket_connection)



# API Service
app = Flask(__name__)
CORS(app)

@app.route('/api/hardware')
def api_hardware():
    uid = request.args.get("uid")
    sid = request.args.get("sid")
    hid = request.args.get("hid")
    if not Database.check_userAuthority(uid, sid, hid): return jsonify({"status" : -1, "msg" : "Access Denied."})
    return jsonify(hardware.query(hid))


@app.route('/api/command')
def api_command():
    uid = request.args.get("uid")
    sid = request.args.get("sid")
    hid = request.args.get("hid")
    cmd = request.args.get("cmd")
    if not Database.check_userAuthority(uid, sid, hid): return jsonify({"status" : -1, "msg" : "Access Denied."})
    return jsonify(iController.IC_command(hid, uid, cmd))


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
            hardware.online(id, type)
            print("%s(%s) : Reporter Online." % (type, id))
            client.send('{"status":0, "msg":"Hello Device."}'.encode("utf8"))
            while True:
                bytes = client.recv(1024)
                if len(bytes) == 0:
                    client.close()
                    hardware.offline(id)
                    print("%s(%s) : Offline"%(type, id))
                    return
                else:
                    hardware.report(id, bytes)
                    iController.IC_report(id)


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
            socket_connection[id] = client

    except: pass


def main():
    # Virtual Init Database
    Database.virtual_init()

    # Init Server
    ADDRESS = ('127.0.0.1', 1024)
    socket_init(ADDRESS)
    server = Thread(target=socket_accept)
    server.setDaemon(True)
    server.start()

    # Init Flask
    app.run()


if __name__ == '__main__': main()