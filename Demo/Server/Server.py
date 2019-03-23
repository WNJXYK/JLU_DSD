import socket, json, time
from multiprocessing import Process, Manager
from threading import Thread
from flask import Flask, request

from Demo.Database import Database
from Demo.Controller import Controller

# Global
manager = Manager()
socket_connection = manager.dict()
socket_server = None
hardware = manager.dict()

# Server Service

def hardware_online(id, type):
    if not id in hardware: hardware[id] = {"online": 0, "type":"???", "data": "Offline", "last": str(time.time())}
    info = hardware[id]
    info["online"] = 1
    info["type"] = type
    info["data"] = "Waiting"
    info["last"] = str(time.time())
    hardware[id] = info

def hardware_offline(id):
    info = hardware[id]
    info["online"] = 0
    info["data"] = "Waiting"
    info["last"] = str(time.time())
    hardware[id] = info

def hardware_report(id, data):
    info = hardware[id]
    info["data"] = json.loads(data)["data"]
    info["last"] = str(time.time())
    hardware[id] = info

def hardware_get(id):
    global hardware
    if not id in hardware: hardware[id] = {"online": 0, "type": "???", "data": "Offline", "last": str(time.time())}
    return hardware[id]

def hardware_query(uid, sid, hid):
    if not Database.check_userAuthority(uid, sid, hid): return '{"status":-1, "msg":"Access Denied."}'
    info = Database.get_hardwareInfo(hid)
    ret = {"id":hid, "nickname":info["nickname"]}
    info = hardware_get(hid)
    ret["online"] = info["online"]
    if info["online"] == 1:
        ret["data"] = info["data"]
        ret["type"] = info["type"]
        ret["last"] = info["last"]
    return ret

# Intelligence Controller
def IC_generateRoom(id):
    # Generate List
    hardwares = Database.get_hardwareList(id)
    device = Database.get_roomDevice(id)
    sensors = []
    for hid in hardwares:
        if device == hid: continue
        sensors.append(hardware_get(hid))
    return sensors, device

def IC_report(id):
    # Get Affected Room
    rooms = Database.get_roomList(id, False)
    for room in rooms:
        sensors, device = IC_generateRoom(room)
        if id == device: continue
        msg = Controller.Run({"sensors":sensors, "device": hardware_get(device), "cmd" : "", "authority": 0})
        print(device, msg)
        try:
            socket_connection[device].send(msg.encode("utf8"))
        except: pass

def IC_command(hid, uid, cmd):
    info = Database.get_hardwareInfo(hid)
    if info["type"] != 1 : return '{"status":-2, "msg":"You can not operate a sensor."}'
    # Get Affected Room
    rooms = Database.get_roomList(hid, False)
    # Get User
    user = Database.get_user(uid)
    for room in rooms:
        print(hid, room)
        sensors, device = IC_generateRoom(room)
        msg = Controller.Cmd({"sensors":sensors, "device": hardware_get(device), "cmd" : cmd, "authority": user["authority"]})
        print(device, msg)
        try:
            socket_connection[device].send(msg.encode("utf8"))
        except:
            return '{"status":-1, "msg":"Device busy or offline."}'

    return '{"status":0, "msg":"Message sent."}'

# Flask
app = Flask(__name__)

@app.route('/api/hardware')
def api_hardware():
    uid = request.args.get("uid")
    sid = request.args.get("sid")
    hid = request.args.get("hid")
    return json.dumps(hardware_query(uid, sid, hid))

@app.route('/api/command')
def api_command():
    uid = request.args.get("uid")
    sid = request.args.get("sid")
    hid = request.args.get("hid")
    cmd = request.args.get("cmd")
    if not Database.check_userAuthority(uid, sid, hid): return json.dumps('{"status":-1, "msg":"Access Denied."}')
    return json.dumps(IC_command(hid, uid, cmd))



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
            hardware_online(id, type)
            print("%s(%s) : Reporter Online." % (type, id))
            client.send('{"status":0, "msg":"Hello Device."}'.encode("utf8"))
            while True:
                bytes = client.recv(1024)
                if len(bytes) == 0:
                    client.close()
                    hardware_offline(id)
                    print("%s(%s) : Offline"%(type, id))
                    return
                else:
                    hardware_report(id, bytes)
                    IC_report(id)


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
    ADDRESS = ('127.0.0.1', 1033)
    socket_init(ADDRESS)
    server = Thread(target=socket_accept)
    server.setDaemon(True)
    server.start()

    # Init Flask
    app.run()


    while True:
        cmd = input()
        if cmd == "Exit":
            socket_server.close()
            exit()
        msg = input()
        if socket_connection[cmd] != None:
            socket_connection[cmd].send(('{"data":"%s"}'%msg).encode("utf8"))


if __name__ == '__main__': main()