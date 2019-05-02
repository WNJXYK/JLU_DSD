import sys, getopt, json
from multiprocessing import Manager
from flask import Flask, request, jsonify
from flask_cors import *
import urllib

sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

from Demo.Controller.Controller import Controller
from Production.Server.Hardware import Hardware
from Production.Server.IController import IController
from Production.Server.Socket import Socket
from Production.Server.IDatabase import IDatabase
from Production.Server.User import User


# Global
manager = Manager()
db = IDatabase()
hardware = Hardware(manager, db)
socket = Socket(manager, hardware, db)
controller = Controller()
iController = IController(hardware, controller, socket, db)
user = User(manager)


# API Service
api = Flask(__name__)
CORS(api)

@api.route('/api/hardware')
def api_hardware():
    # Get Request Parameters
    uid = request.args.get("UID")
    sid = request.args.get("SID")
    hid = request.args.get("HID")

    # Log
    print("Hardware Query (%s, %s): %s" % (uid, sid, hid))

    # Check User's Identification
    if not user.check(str(uid), sid): return jsonify({"status" : -1, "msg" : "Access Denied."})

    # Get Hardware Info
    return jsonify(hardware.query(hid))


@api.route('/api/command')
def api_command():
    # Get Request Parameters
    uid = request.args.get("UID")
    sid = request.args.get("SID")
    hid = request.args.get("HID")
    cmd = request.args.get("CMD")

    # Log
    print("API Command (%s, %s): %s <- %s" % (uid, sid, hid, cmd))

    # Check User's Identification
    if not user.check(str(uid), sid): return jsonify({"status" : -1, "msg" : "Access Denied."})



    # Send Command to IC
    return jsonify(iController.command(hid, uid, cmd))


@api.route('/interface/<task>', methods = ['GET', 'POST'])
def redirect(task):
    DB_SERVER = "http://0.0.0.0:50001"
    url = DB_SERVER + '/user/' + task

    # Log
    print("DB Request %s" % task)


    if task == "login":
        data = None
        if request.method == 'GET': data = request.args.to_dict()
        if request.method == 'POST': data = request.form.to_dict()
        if "email" not in data or "password" not in data: return jsonify({"status": -1, "msg": "Invalid Request"})
        email, password = data["email"], data["password"]

        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko', "Content-Type": "application/x-www-form-urlencoded"}
        req = urllib.request.Request(url=url, data=urllib.parse.urlencode({"email": email, "password": password}).encode(encoding='utf-8'), headers=header_dict)
        res = urllib.request.urlopen(req)
        res = res.read()
        res = res.decode(encoding='utf-8')

        obj = json.loads(res)
        UID = obj["info"]["UID"]
        Nickname = obj["info"]["Nickname"]
        Authority = int(obj["info"]["Authority"])
        SID = user.allocate(str(UID), Nickname , Authority)
        return jsonify({"status": 0, "msg": "Login", "info": {"UID": UID, "SID": SID, "Authority": Authority, "Nickname": Nickname}})

    elif task == "verify":
        data = None
        if request.method == 'GET': data = request.args.to_dict()
        if request.method == 'POST': data = request.form.to_dict()
        if "SID" not in data or "UID" not in data: return jsonify({"status": -1, "msg": "Invalid Request"})

        sid, uid = data["SID"], data["UID"]
        if user.check(str(uid), sid):
            return jsonify({"status": 0, "info": user.get(uid)})
        else:
            return jsonify({"status": -3, "msg":"Invalid User"})

    else:
        data = None
        if request.method == 'GET': data = request.args.to_dict()
        if request.method == 'POST': data = request.form.to_dict()
        if "SID" not in data or "UID" not in data: return jsonify({"status": -1, "msg": "Invalid Request"})
        sid, uid = data["SID"], data["UID"]
        if not user.check(str(uid), sid):
            return jsonify({"status": -3, "msg": "Invalid User"})
        else: print("Go")

        if request.method == 'GET':
            data = urllib.parse.urlencode(request.args.to_dict())
            header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
            req = urllib.request.Request(url='%s%s%s' % (url, '?', data), headers=header_dict)
            res = urllib.request.urlopen(req)
            res = res.read()
            return res

        if request.method == 'POST':
            data = urllib.parse.urlencode(request.form.to_dict()).encode(encoding='utf-8')
            header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                           "Content-Type": "application/x-www-form-urlencoded"}
            req = urllib.request.Request(url=url, data=data, headers=header_dict)
            res = urllib.request.urlopen(req)
            res = res.read()
            return res

    return "Access Denied."



def main():
    # Get Option
    addr = ('0.0.0.0', 8888)
    auth = "WNJXYK"
    opts, args = getopt.getopt(sys.argv[1:], "i:p:k:")
    for op, value in opts:
        if op == "-i": addr = (value, addr[1])
        if op == "-p": addr = (addr[0], int(value))
        if op == "-k": auth = value

    # Init Socket
    socket.run(addr, auth)

    # Heartbeat to IC
    iController.init()
    iController.heartbeat(10)

    # Init API
    api.run(host = '0.0.0.0', port = 8088, threaded=True)

if __name__ == '__main__': main()