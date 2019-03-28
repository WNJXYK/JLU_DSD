import sys, getopt
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

from multiprocessing import Manager
from flask import Flask, request, jsonify
from flask_cors import *

from Demo.Database import Database
from Demo.Controller.Controller import Controller
from Demo.Server.Hardware import Hardware
from Demo.Server.IController import IController
from Demo.Server.Socket import Socket


# Global
manager = Manager()
hardware = Hardware(manager)
socket = Socket(manager, hardware)
controller = Controller()
iController = IController(hardware, controller, socket)

# API Service
api = Flask(__name__)
CORS(api)

@api.route('/api/hardware')
def api_hardware():
    uid = request.args.get("uid")
    sid = request.args.get("sid")
    hid = request.args.get("hid")
    if not Database.check_userAuthority(uid, sid, hid): return jsonify({"status" : -1, "msg" : "Access Denied."})
    return jsonify(hardware.query(hid))


@api.route('/api/command')
def api_command():
    uid = request.args.get("uid")
    sid = request.args.get("sid")
    hid = request.args.get("hid")
    cmd = request.args.get("cmd")
    if not Database.check_userAuthority(uid, sid, hid): return jsonify({"status" : -1, "msg" : "Access Denied."})
    return jsonify(iController.command(hid, uid, cmd))


def main():
    # Virtual Init Database
    Database.virtual_init()

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
    api.run(host = '0.0.0.0', port = 50000, threaded=True)

if __name__ == '__main__': main()