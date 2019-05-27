from flask import Blueprint, jsonify, request
from Server.Database import User
from Server.Database import Hardware
from Server.Database import Room
from Server.Database import Log

api = Blueprint("User_API", __name__)


@api.route("/")
def index():
    return "User API Index"

def check_param(param, data):
    for p in param:
        if p not in data:
            return False, jsonify({"status": -1, "message": "Invalid Request (Missing " + p + ")"})
    return True, ""

def render(request, param, func):
    if request.method == 'GET': data = request.args.to_dict()
    if request.method == 'POST': data = request.form.to_dict()
    for p in param:
        if p not in data:
            return jsonify({"status": -1, "message": "Invalid Request (Missing " + p + ")"})
    return func(data)

@api.route("/login", methods = ['GET', 'POST'])
def login():
    def func(data):
        user, password = data["user"], data["password"]
        status, message, user_object = User.login_user(user, password)

        return jsonify({"status": status, "message": message, "info": user_object})

    return render(request, ["user", "password"], func)

# Query 0， Add 1， Delete 2，Modify 3

@api.route("/user", methods = ['GET', 'POST'])
def user():
    def func(data):
        option, uid, token = int(data["option"]), data["uid"], data["token"]
        if not User.query_permission(uid, token, "admin"): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        if option == 0:
            status, message, info = User.list_user()
            return jsonify({"status": status, "message": message, "info": info})

        if option == 1:
            flag, ret = check_param(["name", "user", "password", "role"], data)
            if not flag: return ret
            name, user, password, role = data["name"], data["user"], data["password"], int(data["role"])
            status, message = User.add_user(user, name, password, role)
            return jsonify({"status": status, "message": message})

        if option == 2:
            flag, ret = check_param(["id"], data)
            if not flag: return ret
            id = data["id"]
            status, message = User.del_user(id)
            return jsonify({"status": status, "message": message})

        if option == 3:
            flag, ret = check_param(["name", "id", "permission", "role"], data)
            if not flag: return ret
            id, name, permission, role = data["id"], data["name"], data["permission"], data["role"]
            status, message = User.modify_user(id, name, role, permission)
            return jsonify({"status": status, "message": message})

        return jsonify({"status": -2, "message": "No Such Command"})


    return render(request, ["option", "uid", "token"], func)

@api.route("/raspi", methods = ['GET', 'POST'])
def raspi():
    def func(data):
        option, uid, token = int(data["option"]), data["uid"], data["token"]
        if not User.query_permission(uid, token, "build"): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        if option == 0:
            status, message, info = Hardware.list_raspi()
            return jsonify({"status": status, "message": message, "info": info})

        if option == 1: return jsonify({"status": -2, "message": "No Such Command"})

        if option == 2:
            flag, ret = check_param(["id"], data)
            if not flag: return ret
            id = data["id"]
            status, message = Hardware.del_raspi(id)
            return jsonify({"status": status, "message": message})

        if option == 3: return jsonify({"status": -2, "message": "No Such Command"})

        return jsonify({"status": -2, "message": "No Such Command"})

    return render(request, ["option", "uid", "token"], func)

@api.route("/hardware", methods = ['GET', 'POST'])
def hardware():
    def func(data):
        option, uid, token = int(data["option"]), data["uid"], data["token"]
        if not User.query_permission(uid, token, ""): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        if option == 0:
            flag, ret = check_param(["room"], data)
            if not flag: return ret
            status, message, info = Room.list_hardware(data["room"])
            return jsonify({"status": status, "message": message, "info": info})

        if not User.query_permission(uid, token, "build"): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        if option == 1:
            flag, ret = check_param(["name", "type", "host", "gpio", "room"], data)
            if not flag: return ret
            name, type, host, gpio, room = data["name"], int(data["type"]), int(data["host"]), data["gpio"], int(data["room"])
            status, message = Hardware.add_hardware(name, type, host, gpio, room)
            return jsonify({"status": status, "message": message})

        if option == 2:
            flag, ret = check_param(["id"], data)
            if not flag: return ret
            id = data["id"]
            status, message = Hardware.del_hardware(id)
            return jsonify({"status": status, "message": message})

        if option == 3: return jsonify({"status": -2, "message": "No Such Command"})

        return jsonify({"status": -2, "message": "No Such Command"})

    return render(request, ["option", "uid", "token"], func)

@api.route("/room", methods = ['GET', 'POST'])
def room():
    def func(data):
        option, uid, token = int(data["option"]), data["uid"], data["token"]
        if not User.query_permission(uid, token, ""): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        if option == 0:
            flag, ret = check_param(["building"], data)
            if not flag: return ret
            status, message, info = Room.list_room(data["building"])
            return jsonify({"status": status, "message": message, "info": info})

        if not User.query_permission(uid, token, "build"): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        if option == 1:
            flag, ret = check_param(["name", "building"], data)
            if not flag: return ret
            name, building = data["name"], int(data["building"])
            status, message = Room.add_room(name, building)
            return jsonify({"status": status, "message": message})

        if option == 2:
            flag, ret = check_param(["id"], data)
            if not flag: return ret
            id = data["id"]
            status, message = Room.del_room(id)
            return jsonify({"status": status, "message": message})

        if option == 3:
            flag, ret = check_param(["id", "name", "timeout", "defaultValue"], data)
            if not flag: return ret
            id, name, timeout, defaultValue = data["id"], data["name"], data["timeout"], data["defaultValue"]
            status, message = Room.modify_room(id, name, timeout, defaultValue)
            return jsonify({"status": status, "message": message})

        return jsonify({"status": -2, "message": "No Such Command"})

    return render(request, ["option", "uid", "token"], func)

@api.route("/building", methods = ['GET', 'POST'])
def building():
    def func(data):
        option, uid, token = int(data["option"]), data["uid"], data["token"]
        if not User.query_permission(uid, token, ""): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        if option == 0:
            status, message, info = Room.list_building()
            return jsonify({"status": status, "message": message, "info": info})

        if not User.query_permission(uid, token, "build"): return jsonify({"status": -1, "message": "Invalid User or Permission"})

        if option == 1:
            flag, ret = check_param(["name"], data)
            if not flag: return ret
            status, message = Room.add_building(data["name"])
            return jsonify({"status": status, "message": message})

        if option == 2:
            flag, ret = check_param(["id"], data)
            if not flag: return ret
            status, message = Room.del_building(data["id"])
            return jsonify({"status": status, "message": message})

        if option == 3: return jsonify({"status": -2, "message": "No Such Command"})

        return jsonify({"status": -2, "message": "No Such Command"})

    return render(request, ["option", "uid", "token"], func)

@api.route("/role", methods = ["GET", "POST"])
def role():
    def func(data):
        option = int(data["option"])

        if option == 0:
            status, message, role = User.query_role()
            return jsonify({"status": status, "message": message, "info": role})

        if option == 3:
            flag, ret = check_param(["uid", "token", "id", "priority"], data)
            if not flag: return ret

            uid, token = data["uid"], data["token"]
            if not User.query_permission(uid, token, "admin"): return jsonify({"status": -1, "message": "Invalid User or Permission"})

            status, message = User.modify_role(data["id"], data["priority"])
            return jsonify({"status": status, "message": message})

        return jsonify({"status": -2, "message": "No Such Command"})

    return render(request, ["option"], func)

@api.route("/log", methods = ['GET', 'POST'])
def log():
    def func(data):
        option = int(data["option"])

        if option == 0:
            status, message, info = Log.list_log()
            return jsonify({"status": status, "message": message, "info": info})

        if option == 2:
            flag, ret = check_param(["uid", "token", "id"], data)
            if not flag: return ret

            uid, token = data["uid"], data["token"]
            if not User.query_permission(uid, token, "admin"): return jsonify({"status": -1, "message": "Invalid User or Permission"})

            status, message = Log.del_log(data["id"])
            return jsonify({"status": status, "message": message})

        return jsonify({"status": -2, "message": "No Such Command"})

    return render(request, ["option"], func)