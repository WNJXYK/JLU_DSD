
from multiprocessing import Manager

from flask import Flask, request, json, jsonify
from flask_cors import *


from Demo.Database import Database
from Demo.Controller.Controller import Controller
from Demo.Server.Hardware import Hardware
from Demo.Server.IController import IController
from Demo.Server.Socket import Socket


# Global
manager = Manager()
socket_connection = manager.dict()
socket_server = None


hardware = Hardware(manager)
socket = Socket(manager, hardware)
controller = Controller()
iController = IController(hardware, controller, socket)



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
    return jsonify(iController.command(hid, uid, cmd))




def main():
    # Virtual Init Database
    Database.virtual_init()

    # Init Server
    socket.run()

    # Init Flask
    app.run()


if __name__ == '__main__': main()