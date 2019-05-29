from flask import Blueprint, jsonify, request
from Server.Database import Hardware
import time, json

api = Blueprint("Hardware_API", __name__)

def render(request, param, func):
    if request.method == 'GET': data = request.args.to_dict()
    if request.method == 'POST': data = request.form.to_dict()
    for p in param:
        if p not in data:
            return jsonify({"status": -1, "message": "Invalid Request (Missing " + p + ")"})
    return func(data)

@api.route("/")
def index():
    return "Hardware API Index"

@api.route("/allocate", methods = ['GET', 'POST'])
def allocate():
    def func(data):
        if "name" in data:
            status, message, uid = Hardware.add_raspi(data["name"])
        else:
            status, message, uid = Hardware.add_raspi()
        print(" * Server : Allocate new raspi " + uid)
        return jsonify({"status": status, "message": message, "info": uid})
    return render(request, [], func)

@api.route("/report", methods = ['GET', 'POST'])
def report():
    def func(data):
        uid, data = data["uid"], data["content"]
        id = Hardware.query_raspi_id(uid)
        if id < 0: return jsonify({"status": -2, "message": "No such Raspi uid"})
        data = Hardware.update_raspi(id, json.loads(data), time.time())
        print(" * Hardware : Send to Raspi ", uid, data)
        return jsonify({"status": 0, "message": "", "info": data})
    return render(request, ["uid", "content"], func)
