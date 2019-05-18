import sys, getopt, json
from multiprocessing import Manager
from flask import Flask, request, jsonify
from flask_cors import *
import urllib
import Config

sys.path.append(sys.path[0] + "/..")

from Hardware import Hardware
from IController import IController
from Socket import Socket
from IDatabase import IDatabase
from User import User


# Global
manager = Manager()
db = IDatabase()
hardware = Hardware(manager, db)
socket = Socket(manager, hardware, db)
iController = IController(hardware, socket, db)
user = User(manager)


# API Service
api = Flask(__name__)
CORS(api)

@api.errorhandler(404)
def page_not_found(e):
    return "Opsss. This is a private page."

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
    url = Config.DBServer + '/user_' + task

    # Log
    print("DB Request %s" % task)


    if task == "login":
        data = None
        if request.method == 'GET': data = request.args.to_dict()
        if request.method == 'POST': data = request.form.to_dict()
        print(request.method, data)
        if "UID" not in data or "password" not in data: return jsonify({"status": -1, "msg": "Invalid Request"})
        UID, password = data["UID"], data["password"]
        print(UID, password)

        try:
            header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                           "Content-Type": "application/x-www-form-urlencoded"}
            req = urllib.request.Request(url=url,
                                         data=urllib.parse.urlencode({"UID": UID, "password": password}).encode(
                                             encoding='utf-8'), headers=header_dict)
            res = urllib.request.urlopen(req)
            res = res.read()
            res = res.decode(encoding='utf-8')
            obj = json.loads(res)

            if obj["status"] == 1:
                return jsonify({"status": -1, "msg": "Login Failed"})
            elif obj["status"] == 0:
                name = obj["user"]["name"]
                role = int(obj["user"]["role"])
                SID = user.allocate(str(UID), name, role)
                return jsonify(
                    {"status": 0, "msg": "Login", "info": {"UID": UID, "SID": SID, "Nickname": name, "Role": role}})
            else:
                return jsonify({"status": -2, "msg": "DB ERROR"})
        except Exception as err:
            return jsonify({"status": -3, "msg": err})

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

        print("DBRequest", url, data)

        if not user.check(str(uid), sid):
            return jsonify({"status": -3, "msg": "Invalid User"})
        else: print("Go")

        if request.method == 'GET':
            data = urllib.parse.urlencode(request.args.to_dict())
            header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
            req = urllib.request.Request(url='%s%s%s' % (url, '?', data), headers=header_dict)
            res = urllib.request.urlopen(req)
            res = res.read()
            print("DB Request", res)
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
    iController.heartbeat(30)

    # Init API
    api.run(host = '0.0.0.0', port = 8088, threaded=True)


if __name__ == '__main__': main()