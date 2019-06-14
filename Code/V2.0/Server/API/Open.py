from flask import Blueprint, jsonify, request
from Server.Database import User
from Server.Database import Room
from Server.Database import Hardware
from Server.Controller import IController

api = Blueprint("Open_API", __name__)

def render(request, param, func):
    if request.method == 'GET': data = request.args.to_dict()
    if request.method == 'POST': data = request.form.to_dict()
    for p in param:
        if p not in data:
            return jsonify({"status": -1, "message": "Invalid Request (Missing " + p + ")"})
    return func(data)

@api.route("/")
def index():
    return "Open API Index"

# This API is Legacy
@api.route("/role", methods = ['GET', 'POST'])
def role():
    def func(data):
        status, message, role = User.query_role()
        return jsonify({"status": status, "message": message, "info": role})

    return render(request, [], func)

@api.route("/overall", methods = ['GET', 'POST'])
def overall():
    def func(data):
        ret = {
            "Users : ": User.query_user_count()[2],
            "Rooms : ": Room.query_room_count()[2],
            "Buildings : ": Room.query_building_count()[2],
            "Raspi : ": Hardware.query_raspi_count()[2],
            "Hardware : ": Hardware.query_hardware_count()[2]
        }
        return jsonify({"status": 0, "message": "", "info": ret})

    return render(request, [], func)

