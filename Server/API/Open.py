from flask import Blueprint, jsonify, request
from Server.Database import User
from Server.Database import Room
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

@api.route("/role", methods = ['GET', 'POST'])
def status():
    def func(data):
        status, message, role = User.query_role()
        return jsonify({"status": status, "message": message, "info": role})

    return render(request, [], func)


