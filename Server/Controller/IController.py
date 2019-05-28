from urllib import parse, request
from Server.Database import Room
from Server.Database import Hardware
from Server.Database import IDatabase
from Server.Database import Log
from Server.Database import User
import time, json
from Server import Config

def post(url, data):
    data = parse.urlencode(data).encode(encoding='utf-8')
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                   "Content-Type": "application/x-www-form-urlencoded"}
    req = request.Request(url=url, data=data, headers=header_dict)
    res = request.urlopen(req)
    res = res.read().decode("utf-8")
    return res


def command(command, priority, force_flag):
    obj = json.loads(command)
    hardware, value, type = obj["hardware"], obj["value"], obj["type"]

    hardware = Hardware.query_hardware(hardware)[2]
    room_id = Room.query_room(hardware["room"])[2]["id"]
    command = json.dumps({"hardware": hardware["id"], "value":value, "type": type if force_flag else ""})
    print(command)
    return send(room_id, command, priority)


def heart_beat():
    _, _, building_list = Room.list_building()
    for building in building_list:
        building_id, building_status = building["id"], building["status"]
        _, _, room_list = Room.list_room(building_id)
        for room in room_list:
            send(room["id"])


def send(room_id, command = "", priority = 0):
    # Query Rooms
    _, _, room = Room.query_room(room_id)
    room_id, room_timeout, room_defaultValue, room_status, room_building = room["id"], room["timeout"], room["defaultValue"], room["status"], room["building"]

    # Get All Hardwares
    _, _, hardware_list = Room.list_hardware(room_id)
    params = {"time":time.time(),
              "building": room_building,
              "room": room_id,
              "timeout": room_timeout,
              "default": room_defaultValue,
              "status": room_status,
              "sensors":[],
              "devices":[],
              "command": command,
              "priority": priority}

    for hardware in hardware_list:
        id, type, func, value = hardware["id"], hardware["type_id"], hardware["func"], hardware["value"]
        if int(func) == 1:
            params["devices"].append({"id": id, "type": type, "value": value})
        else:
            params["sensors"].append({"id": id, "type": type, "value": value})

    # Request
    try:
        _, addr = IDatabase.render("SELECT value FROM Config WHERE name = ?", (Config.CONTROLLER_ADDRESS_NAME,))
        res = post(addr[0][0], {"info" : json.dumps(params)})
        res = json.loads(res)
        for p in res["command"]: eval(p)

        try:
            Config.LAST_COMMAND.append({"Input":params, "Output":res})
        except: pass

        return res["status"], res["message"]
    except Exception as err:
        print(" * Controller : " + str(err))
        return 1, str(err)



