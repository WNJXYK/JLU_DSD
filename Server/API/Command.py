from flask import Blueprint, jsonify, request
from Server.Database import User
from Server.Database import Room
from Server.Controller import IController

api = Blueprint("Command_API", __name__)

def render(request, param, func):
    if request.method == 'GET': data = request.args.to_dict()
    if request.method == 'POST': data = request.form.to_dict()
    for p in param:
        if p not in data:
            return jsonify({"status": -1, "message": "Invalid Request (Missing " + p + ")"})
    return func(data)

@api.route("/")
def index():
    return "Command API Index"

@api.route("/status", methods = ['GET', 'POST'])
def status():
    def func(data):
        uid, token, id, stus = data["uid"], data["token"], data["id"], data["status"]
        if not User.query_permission(uid, token, "admin"): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        status, message = Room.modify_building_status(id, stus)
        return jsonify({"status": status, "message": message})

    return render(request, ["uid", "token", "id", "status"], func)

@api.route("/command", methods = ['GET', 'POST'])
def command():
    def func(data):
        uid, token, command = data["uid"], data["token"], data["command"]
        if not User.query_permission(uid, token, ""): return jsonify({"status": -1, "message": "Invalid User or Permission"})
        user = User.query_user(uid)[2]
        status, message = IController.command(command, user["priority"], User.query_permission(uid, token, "force"))
        return jsonify({"status": status, "message": message})

    return render(request, ["uid", "token", "command"], func)



