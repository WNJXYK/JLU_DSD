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
        data = json.loads(data["info"])
        time = data["time"]
        timeout = data["timeout"]
        priority = data["priority"]
        command = data["command"]
        room_status = data["status"]
        default_value = int(data["default"])
        command_list = []
        operate_flag = False
        nop_flag = True

        # Solve Command
        if len(command)>0:
            nop_flag = False
            command = json.loads(command)
            hid, val, typ = str(command["hardware"]), command["value"], command["type"]
            if hid not in mem:
                if typ == "force":
                    mem[hid] = {"priority" : 0, "force": 1, "last": time}
                else:
                    mem[hid] = {"priority": priority, "force": 0, "last": time}
                operate_flag = True
            else:
                if typ == "force":
                    mem[hid] = {"priority": 0, "force": 1, "last": time}
                    operate_flag = True
                else:
                    if (int(mem[hid]["priority"])<=int(priority) and int(mem[hid]["force"])==0) or float(time)-float(mem[hid]["last"])>float(timeout):
                        mem[hid] = {"priority": priority, "force": 0, "last": time}
                        operate_flag = True
            if operate_flag: command_list.append("Hardware.set_light(%s, %s)" % (hid, str(val)))

        present_flag = False
        light_flag = False
        button_flag = False
        panic_flag = False

        for s in data["sensors"]:
            hid, typ, val = str(s["id"]), int(s["type"]), int(s["value"])
            if hid not in mem: mem[hid] = {"value": val}
            if typ == 3 and val == 0: light_flag = True
            if typ == 4 and val == 1: present_flag = True
            if typ == 5 and mem[hid]["value"] == 0 and val == 1: button_flag = True
            if typ == 6 and mem[hid]["value"] == 0 and val == 1: panic_flag = True
            mem[hid] = {"value": val}

        keep_alive = present_flag and light_flag

        # Panic Switch
        if panic_flag: command_list.append("Log.add_log(%s, %s)" % (data["building"], data["room"]))

        # Solve Light
        for s in data["devices"]:
            hid, typ, val = str(s["id"]), int(s["type"]), int(s["value"])
            if hid not in mem:
                mem[hid] = {"priority" : 0, "force": 0, "last": time}
                command_list.append("Hardware.set_light(%s, %s)" % (hid, default_value))

            # Emergency : Open Light
            if room_status != 0 or panic_flag:
                command_list.append("Hardware.set_light(%s, %s)" % (hid, 1))
                mem[hid]["last"] = time
            else:
                # Close Emergency Light
                if typ == 2: command_list.append("Hardware.set_light(%s, 0)" % hid)

                # Solve Button
                if button_flag and typ == 1:
                    command_list.append("Hardware.set_light(%s, %s)" % (hid, str(1-val)))
                    mem[hid]["last"] = time

                # Light KeepAlive When People There
                if typ == 1 and val == 1 and keep_alive:
                    mem[hid]["last"] = time

                # Light Timeout When No People
                if typ == 1 and val == 1 and (not keep_alive) and float(time)-float(mem[hid]["last"])>float(timeout):
                    if ("force" in mem[hid]) and int(mem[hid]["force"]) == 1:
                        pass
                    else:
                        command_list.append("Hardware.set_light(%s, 0)" % hid)

        if operate_flag or nop_flag: return jsonify({"status":0, "message":"", "command": command_list})

        return jsonify({"status": 1, "message": "Permission Denied", "command": command_list})


    return render(request, [], func)



