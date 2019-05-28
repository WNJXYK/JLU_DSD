from flask import Blueprint, jsonify, request
from Server.Database import IDatabase
import time, json
from Server import Config

api = Blueprint("Debug_API", __name__)


def render(request, param, func):
    if request.method == 'GET': data = request.args.to_dict()
    if request.method == 'POST': data = request.form.to_dict()
    for p in param:
        if p not in data:
            return jsonify({"status": -1, "message": "Invalid Request (Missing " + p + ")"})
    return func(data)


@api.route("/")
def index():
    return "Debug API Index"


def set_control_addr(addr):
    IDatabase.render("UPDATE Config SET value = ? WHERE name = ?", (addr, Config.CONTROLLER_ADDRESS_NAME,))


@api.route("/reset_addr", methods = ['POST'])
def reset_addr():
    if request.method != 'POST': return "Access Denied."
    set_control_addr("http://0.0.0.0:8088/control/control")
    return "Set Controller Address to " + "http://0.0.0.0:8088/control/control"


@api.route("/set_addr", methods = ['POST'])
def set_addr():
    if request.method != 'POST': return "Access Denied."
    data = request.form.to_dict()
    if "address" not in data or "password" not in data: return "Access Denied."
    if data["password"] != "Qwerty123": return "Wrong Password."
    set_control_addr(data["address"])
    return "Set Controller Address to " + data["address"]


@api.route("/setting", methods = ['GET'])
def setting():
    _, addr = IDatabase.render("SELECT value FROM Config WHERE name = ?", (Config.CONTROLLER_ADDRESS_NAME,))
    return '''<html><body>
        <form action="/debug/set_addr" method="post">
          Controller Address : <input type="text" name="address" value="''' + addr[0][0] + '''"/><br>
          Password : <input type="password" name="password"/><br>
          <input type="submit" value="Submit" />
        </form>
        <form action="/debug/reset_addr" method="post">
          Reset Controller Address to localhost : 
          <input type="submit" value="Reset" />
        </form>
        </body>
        </html>'''


@api.route("/last")
def last():
    ret = []
    try:
        while True:
            ret.append(Config.LAST_COMMAND.popleft())
    except:
        Config.LAST_COMMAND.clear()
    return jsonify(ret)