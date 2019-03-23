import hashlib

hardware = {}
hardware_room = {}
room_hardware = {}
room_device = {}
user = {}
user_room = {}

def virtual_init():
    hardware["qwerty"] = {"type":"LightDevice", "nickname":"寝室灯", "hardware": 1}
    hardware["popoqqq"] = {"type": "Camera", "nickname": "寝室摄像头", "hardware": 0}

    hardware_room["qwerty"] = ["0001"]
    hardware_room["popoqqq"] = ["0001"]
    room_hardware["0001"] = ["qwerty", "popoqqq"]
    room_device["0001"] = "qwerty"

    user["admin"] = { "password":"admin", "nickname":"管理员", "authority" : 3 , "email":"admin@admin.com", "sid":"", "code":""}
    user["wnjxyk"] = {"password": "wnjxyk", "nickname": "喂你脚下有坑", "authority": 2, "email": "wnjxyk@gmail.com", "sid": "", "code":""}

    user_room["wnjxyk"] = ["0001"]

# Hardware

def is_hardware(id): return (id in hardware)
def is_device(id): return ((id in hardware) and (hardware[id]["hardware"]==1))

# Params: User Id
# Return: Room Id List
def get_roomList(id):
    if not id in hardware: return []
    return hardware[id]

# Params: Room Id
# Return: Hardware Id List
def get_hardwareList(id):
    if not id in room_hardware: return []
    return room_hardware[id]

# Params: Hardware Id
# Return: Hardware Info
def get_roomDevice(id):
    if not id in room_device: return ""
    return room_device[id]

# Params: Hardware Id
# Return: Hardware Info
def get_hardwareInfo(id):
    if not id in hardware: return {}
    return hardware[id]

# User

def user_newUser(id, info):
    if id in user: return '{"status":-1, "msg":"User is existed"}'
    user[id]=info
    return '{"status":0, "msg":"Hello"}'
def user_modifyInfo(id, info, passwd):
    if user[id]["password"] != passwd: return '{"status":-1, "msg":"Incorrect Password"}'
    for key in info:
        if key=="sid" or key=="authority" or key=="code" or key not in user[id]: continue
        user[id][key]=info[key]
    return '{"status":0, "msg":"User Information Updated"}'
def user_modifyAuthority(id, auth, admin_id, admin_sid):
    if (admin_id in user) and (user[admin_id]["sid"]==admin_sid):
        if id in user:
            user[id]["authority"] = auth
            return '{"status":0, "msg":"Authority Updated"}'
        else:
            return '{"status":-2, "msg":"%s Is Not Found"}' % id
    else:
        return '{"status":-1, "msg":"Need An Admin Account"}'

def user_forgetPassword(id, email):
    if not id in user: '{"status":-1, "msg":"%s Is Not Found"}' % id
    if email != user[id]["email"]: '{"status":-1, "msg":"Incorrect Email"}'
    # Generate Code & Send Email
    return '{"status":0, "msg":"An Email Is Sent To %s"}' % email
def user_forgetPasswordCheck(id, code):
    if not id in user: '{"status":-1, "msg":"Page Not Found"}'
    if user[id]["code"] != code : '{"status":-1, "msg":"Page Not Found"}'
    return '{"status":0, "msg":"%s"}' % user[id]["password"]

# App

def checkAuthority(id, sid):
    if not id in user: return False
    if user[id]["authority"] != 4 or user[id]["sid"]!=sid: return False
    return True

def user_addHardware2Room(uid, sid, hid, rid):
    if not checkAuthority(uid, sid): return '{"status":-1, "msg":"Need An Admin Account"}'
    if hid in hardware_room[rid]: return '{"status":-2, "msg":"Hardware %s Has Been Already In Room %s"}' % (hid, rid)
    if room_device[rid] != None and hardware[hid]["hardware"]==1: return '{"status":-3, "msg":"Room %s Has Already Had A Device"}' % rid
    if not hid in hardware_room:
        hardware_room[hid] = [rid]
    else:
        hardware_room[hid].append(rid)
    room_hardware[rid].append(hid)
    if hardware[hid]["hardware"] == 1: room_device[rid]=hid
    return '{"status":0, "msg":"Hardware %s has been added to Room %s successfully"}' % (hid, rid)

def user_removeHardware2Room(uid, sid, hid, rid):
    if not checkAuthority(uid, sid): return '{"status":-1, "msg":"Need An Admin Account"}'
    if not hid in hardware_room[rid]: return '{"status":-2, "msg":"Hardware %s Has Already Been Removed From Room %s"}' % (hid, rid)

    hardware_room[hid].remove(rid)
    room_hardware[rid].remove(hid)
    if hardware[hid]["hardware"] == 1: room_device[rid] = None
    return '{"status":0, "msg":"Hardware %s has been removed from Room %s successfully"}' % (hid, rid)
