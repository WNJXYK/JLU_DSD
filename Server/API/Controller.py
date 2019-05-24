from flask import Blueprint, jsonify, request
import json

api = Blueprint("Control_API", __name__)

def render(request, param, func):
    if request.method == 'GET': data = request.args.to_dict()
    if request.method == 'POST': data = request.form.to_dict()
    for p in param:
        if p not in data:
            return jsonify({"status": -1, "message": "Invalid Request (Missing " + p + ")"})
    return func(data)

@api.route("/")
def index():
    return "Controller API Index"


mem = {}

@api.route("/control", methods = ['GET', 'POST'])
def control():
    def func(data):
        global mem
        time = data["time"]
        timeout = data["time"]
        priority = data["priority"]
        command = data["command"]
        if len(command)>0:
            command = json.loads(command)
            hid, val, typ = str(command["hardware"]), command["value"], command["type"]
            flag = False
            if hid not in mem:
                if typ == "force":
                    mem[hid] = {"priority" : 0, "force": 1, "last": time}
                else:
                    mem[hid] = {"priority": priority, "force": 0, "last": time}
                flag = True
            else:
                if typ == "force":
                    mem[hid] = {"priority": 0, "force": 1, "last": time}
                    flag = True
                else:
                    if mem[hid]["priority"]<=priority or time-mem[hid]["last"]>timeout:
                        mem[hid] = {"priority": priority, "force": 0, "last": time}
                        flag = True
            if flag: return jsonify({"status":0, "message":"", "command":["Hardware.set_light(%s, %s)" % (hid, str(val))]})

            return jsonify({"status":1, "message":"Permission Denied"})
        else:
            return jsonify({"status":0, "message":"", "command":[]})


    return render(request, [], func)



