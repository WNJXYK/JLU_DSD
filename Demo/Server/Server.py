import sys, getopt
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

from multiprocessing import Manager
from flask import Flask, request, jsonify
from flask_cors import *

import urllib

# from Demo.Database import Database
from Demo.Controller.Controller import Controller
from Demo.Server.Hardware import Hardware
from Demo.Server.IController import IController
from Demo.Server.Socket import Socket
from Demo.Server.IDatabase import IDatabase


# Global
manager = Manager()
db = IDatabase()
hardware = Hardware(manager, db)
socket = Socket(manager, hardware, db)
controller = Controller()
iController = IController(hardware, controller, socket, db)
DB_SERVER = "http://0.0.0.0:50001"

# API Service
api = Flask(__name__)
CORS(api)

@api.route('/api/hardware')
def api_hardware():
    uid = request.args.get("uid")
    sid = request.args.get("sid")
    hid = request.args.get("hid")
    if not db.checkUserHardware(uid, sid, hid): return jsonify({"status" : -1, "msg" : "Access Denied."})
    return jsonify(hardware.query(hid))


@api.route('/api/command')
def api_command():
    uid = request.args.get("uid")
    sid = request.args.get("sid")
    hid = request.args.get("hid")
    cmd = request.args.get("cmd")
    if not db.checkUserHardware(uid, sid, hid): return jsonify({"status" : -1, "msg" : "Access Denied."})
    return jsonify(iController.command(hid, uid, cmd))


@api.route('/interface/<typ>/<task>', methods = ['GET', 'POST'])
def redirect(typ, task):
    global DB_SERVER
    url = DB_SERVER + '/' + typ + '/' + task

    if request.method == 'GET':
        data = urllib.parse.urlencode(request.args.to_dict())
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
        req = urllib.request.Request(url='%s%s%s' % (url, '?', data), headers=header_dict)
        res = urllib.request.urlopen(req)
        res = res.read()
        return res

    if request.method == 'POST':
        data = urllib.parse.urlencode(request.form.to_dict()).encode(encoding='utf-8')
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko', "Content-Type": "application/x-www-form-urlencoded"}
        req = urllib.request.Request(url=url, data=data, headers=header_dict)
        res = urllib.request.urlopen(req)
        res = res.read()
        return res

    return "Access Denied."



def main():
    # Virtual Init Database
    # Database.virtual_init()

    # Get Option
    addr = ('0.0.0.0', 1024)
    auth = "WNJXYK"
    opts, args = getopt.getopt(sys.argv[1:], "i:p:k:")
    for op, value in opts:
        if op == "-i": addr = (value, addr[1])
        if op == "-p": addr = (addr[0], int(value))
        if op == "-k": auth = value

    # Init Socket
    socket.run(addr, auth)

    # Heartbeat to IC
    iController.heartbeat(5)

    # Init API
    api.run(host = '0.0.0.0', port = 443, threaded=True)

if __name__ == '__main__': main()