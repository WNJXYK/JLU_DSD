import os, sys, getopt
import traceback
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

import hashlib, sqlite3, time
from flask import Flask, request, jsonify
from flask_cors import *
from Simulate.Database import DBInit

# Constant
PATH = "./database.db"
QUERY_ROOM_AUTHORITY = 2
MODIFY_ROOM_AUTHORITY = 4
MODIFY_HARDWARE_AUTHORITY = 4
SENSOR_TYPE = ["PresenceSensor", "LightSensor", "ButtonSensor"]
DEVICE_TYPE = ["Light"]

# API Service
api = Flask(__name__)
CORS(api)

def md5(s):
    ret = hashlib.md5()
    ret.update(s.encode("utf8"))
    return ret.hexdigest()

def db_connection(name, params, func):
    try:
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        ret = func(c, conn, params)
        return ret
    except Exception as err:
        print(name, err)
        traceback.print_stack()
        return jsonify({"status": -2, "msg": "Server Error : " + str(err)})
    finally:
        c.close()
        conn.close()

# 用户登陆
@api.route('/user/login', methods = ['GET', 'POST'])
def user_login():

    try:
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        email = None
        password = None
        if request.method == 'GET':
            email = request.args.get('email')
            password = request.args.get('password')
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
        if email is None or password is None:
            return jsonify({"status": -1, "msg": "Invalid Request"})

        print("Login", email, password)

        cursor = c.execute("SELECT UID, Authority, Nickname from User where Email=? and Password=?", (email, password))
        res = cursor.fetchone()

        if res is None:
            return jsonify({"status":-3, "msg":"Incorrect Email or Password"})

        UID, Authority, Nickname = res[0], res[1], res[2]
        SID = md5(str(time.time()) + password)

        c.execute("UPDATE User SET SID = '%s' WHERE UID = %d" % (SID, UID))
        conn.commit()

        return jsonify({"status": 0, "msg": "Login", "info": {"UID": UID, "SID": SID, "Authority": Authority, "Nickname": Nickname}})

    except Exception as err:
        print("Login", err)
        return jsonify({"status": -2, "msg": "Server Error"})

    finally:
        c.close()
        conn.close()


# 用户验证登陆状态
@api.route('/user/verify', methods = ['GET', 'POST'])
def user_verify():
    try:
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        UID = None
        SID = None
        if request.method == 'GET':
            UID = request.args.get('UID')
            SID = request.args.get('SID')
        if request.method == 'POST':
            UID = request.form.get('UID')
            SID = request.form.get('SID')
        if UID is None or SID is None:
            return jsonify({"status": -1, "msg": "Invalid Request"})

        # print("Verify", UID, SID)

        cursor = c.execute("SELECT UID, Authority, Nickname from User where UID=?", (UID, ))
        res = cursor.fetchone()

        if res is None: return jsonify({"status":-3, "msg":"Invalid User"})

        UID, Authority, Nickname = res[0], res[1], res[2]
        Admin = 0 if Authority < MODIFY_HARDWARE_AUTHORITY else 1
        return jsonify({"status": 0, "msg": "Valid User", "info": {"UID": UID, "Authority": Authority, "Nickname": Nickname, "Admin": Admin}})

    except Exception as err:
        print("Verify", err)
        return jsonify({"status": -2, "msg": "Server Error"})

    finally:
        c.close()
        conn.close()

# 获取用户可查看房间
@api.route('/user/room', methods = ['GET', 'POST'])
def user_room():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID = params["SID"], params["UID"]
        BID, Offset, Delta = None, 0, 10
        if "Offset" in params: Offset = params["Offset"]
        if "Delta" in params: Delta = params["Delta"]
        if "BID" in params: BID = params["BID"]
        if BID == "0": BID = None

        cursor = c.execute("SELECT Authority from User where UID=?", (UID, ))
        res = cursor.fetchone()
        if res is None: return jsonify({"status":-3, "msg":"Invalid User"})
        Authority = res[0]

        cnt = 0
        if Authority >= QUERY_ROOM_AUTHORITY:
            if BID is not None:
                cursor = c.execute("SELECT COUNT(*) FROM Room WHERE BID = ?", (BID,))
            else:
                cursor = c.execute("SELECT COUNT(*) FROM Room")
        else:
            if BID is None:
                cursor = c.execute("SELECT COUNT(*) FROM Room \
                               WHERE RID IN (SELECT DISTINCT RID FROM rUser WHERE UID = ?)", (UID,))
            else:
                cursor = c.execute("SELECT COUNT(*) FROM Room \
                                               WHERE RID IN (SELECT DISTINCT RID FROM rUser WHERE UID = ?) and BID = ?", (UID, BID))
        cnt = cursor.fetchone()[0]

        if Authority >= QUERY_ROOM_AUTHORITY:
            if BID is not None:
                cursor = c.execute("SELECT RID, Nickname, SensorCNT, DeviceCNT, Details, BID FROM Room WHERE BID = ? LIMIT ? OFFSET ?", (BID, Delta, Offset))
            else:
                cursor = c.execute("SELECT RID, Nickname, SensorCNT, DeviceCNT, Details, BID FROM Room LIMIT ? OFFSET ?", (Delta, Offset))
        else:
            if BID is not None:
                cursor = c.execute("SELECT RID, Nickname, SensorCNT, DeviceCNT, Details, BID FROM Room \
                               WHERE RID IN (SELECT DISTINCT RID FROM rUser WHERE UID = ?) and BID = ? LIMIT ? OFFSET ?", (UID, BID, Delta, Offset))
            else:
                cursor = c.execute("SELECT RID, Nickname, SensorCNT, DeviceCNT, Details, BID FROM Room \
                                               WHERE RID IN (SELECT DISTINCT RID FROM rUser WHERE UID = ?) LIMIT ? OFFSET ?", (UID, Delta, Offset))

        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append({"RID": res[0], "Nickname": res[1], "sCNT": res[2], "dCNT": res[3], "Details": res[4], "BID": res[5]})

        auth = 0
        if Authority >= MODIFY_ROOM_AUTHORITY: auth = 1

        return jsonify({"status": 0, "info": {"arr":ret, "cnt":cnt, "Modify": auth}})

    if request.method == 'GET':
        return db_connection("Room", request.args.to_dict(), func)
    if request.method == 'POST':
        return db_connection("Room", request.form.to_dict(), func)

# 修改房间
@api.route('/user/modify_room', methods = ['GET', 'POST'])
def user_modify_room():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params) or ("RID" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID, RID = params["SID"], params["UID"], params["RID"]
        Delete, Details, BID = 0, None, None
        if "Delete" in params: Delete = int(params["Delete"])
        if "Details" in params: Details = params["Details"]
        if "BID" in params: BID = int(params["BID"])

        cursor = c.execute("SELECT Authority from User where UID=?", (UID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < MODIFY_ROOM_AUTHORITY: return jsonify({"status": -4, "msg": "Invalid Authority"})

        if Delete == 1:
            c.execute("DELETE from Room where RID=?", (RID,))
            c.execute("DELETE from rUser where RID=?", (RID,))
            c.execute("DELETE from rHardware where RID=?", (RID,))
            conn.commit()
        else:
            c.execute("UPDATE Room set Details = ? , BID = ? where RID=?", (Details, BID, RID))
            conn.commit()
        return jsonify({"status": 0, "info": conn.total_changes})

    if request.method == 'GET': return db_connection("Modify_Room", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Modify_Room", request.form.to_dict(), func)

# 增加房间
@api.route('/user/add_room', methods = ['GET', 'POST'])
def user_add_room():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params) or ("Nickname" not in params) or ("Details" not in params) or ("BID" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID, Nickname, Details, BID = params["SID"], params["UID"], params["Nickname"], params["Details"], params["BID"]

        cursor = c.execute("SELECT Authority from User where UID=?", (UID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < MODIFY_ROOM_AUTHORITY: return jsonify({"status": -4, "msg": "Invalid Authority"})

        sql = "INSERT INTO Room (Nickname, SensorCNT, DeviceCNT, Details, BID) VALUES ('%s', 0, 0, '%s', %d)" %(str(Nickname), str(Details), int(BID))

        c.execute(sql)

        conn.commit()
        return jsonify({"status": 0, "info": conn.total_changes})

    if request.method == 'GET': return db_connection("Add_Room", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Add_Room", request.form.to_dict(), func)

# 查询房间硬件
@api.route('/user/hardware', methods = ['GET', 'POST'])
def user_hardware():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params) or ("RID" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID, RID = params["SID"], params["UID"], params["RID"]

        cursor = c.execute("SELECT Authority from User where UID=?", (UID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < QUERY_ROOM_AUTHORITY:
            cursor = c.execute("SELECT * rUser from User where UID=? and RID=?", (UID, RID))
            res = cursor.fetchone()
            if res is None: return jsonify({"status": -4, "msg": "Invalid Authority"})

        cursor = c.execute("SELECT HID, Nickname, Type, Ctrl FROM Hardware\
                  WHERE HID IN (SELECT HID FROM rHardware WHERE RID=?)", (RID,))

        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append({"HID": res[0], "Nickname": res[1], "Type": res[2], "Ctrl": res[3]})

        conn.commit()
        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET': return db_connection("Hardware", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Hardware", request.form.to_dict(), func)

# 查询房间硬件
@api.route('/user/allHardware', methods = ['GET', 'POST'])
def user_allHardware():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID = params["SID"], params["UID"]

        cursor = c.execute("SELECT Authority from User where UID=?", (UID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < MODIFY_HARDWARE_AUTHORITY: return jsonify({"status": -4, "msg": "Invalid Authority"})

        cursor = c.execute("SELECT HID, Nickname, Type, Ctrl FROM Hardware")

        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append({"HID": res[0], "Nickname": res[1], "Type": res[2], "Ctrl": res[3]})

        conn.commit()
        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET': return db_connection("Hardware", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Hardware", request.form.to_dict(), func)

# 查询房间硬件
@api.route('/user/del_hardware', methods = ['GET', 'POST'])
def user_del_Hardware():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params) or ("HID" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID, HID = params["SID"], params["UID"], params["HID"]

        cursor = c.execute("SELECT Authority from User where UID=?", (UID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < MODIFY_HARDWARE_AUTHORITY: return jsonify({"status": -4, "msg": "Invalid Authority"})

        c.execute("DELETE from Hardware where HID=?", (HID,))
        c.execute("DELETE from rHardware where HID=?", (HID,))

        conn.commit()
        return jsonify({"status": 0, "info": conn.total_changes})

    if request.method == 'GET': return db_connection("Hardware", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Hardware", request.form.to_dict(), func)

# 增加硬件设备
@api.route('/user/add_hardware', methods = ['GET', 'POST'])
def user_add_hardware():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params) or ("HID" not in params) or ("Type" not in params) or ("Nickname" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID, HID, Type, Nickname = params["SID"], params["UID"], params["HID"], params["Type"], params["Nickname"]

        cursor = c.execute("SELECT Authority from User where UID=?", (UID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < MODIFY_HARDWARE_AUTHORITY: return jsonify({"status": -4, "msg": "Invalid Authority"})
        if Type not in SENSOR_TYPE and Type not in DEVICE_TYPE: return jsonify({"status": -5, "msg": "Invalid Type"})

        sql = "INSERT INTO Hardware (HID, Nickname, Type, Ctrl) VALUES ('%s', '%s', '%s', %d)"%(str(HID), str(Nickname), str(Type), (1 if Type in DEVICE_TYPE else 0))
        c.execute(sql)

        conn.commit()
        return jsonify({"status": 0})

    if request.method == 'GET': return db_connection("Add Hardware", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Add Hardware", request.form.to_dict(), func)

# 绑定硬件与房间
@api.route('/user/bind_hardware', methods = ['GET', 'POST'])
def user_bind_hardware():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params) or ("HID" not in params) or ("RID" not in params) or ("Bind" not in params) : return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID, HID, RID, Bind = params["SID"], params["UID"], params["HID"], params["RID"], int(params["Bind"])

        cursor = c.execute("SELECT Authority from User where UID=?", (UID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < MODIFY_HARDWARE_AUTHORITY: return jsonify({"status": -4, "msg": "Invalid Authority"})

        # No Hardware
        cursor = c.execute("SELECT HID from Hardware where HID = ?", (HID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -7, "msg": "No such hardware"})

        # No Room
        cursor = c.execute("SELECT RID from Room where RID=?", (RID,))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -8, "msg": "No such room"})

        # Already Bind / Unbind
        cursor = c.execute("SELECT HID from rHardware where HID=? and RID=?", (HID, RID))
        res = cursor.fetchone()
        if Bind == 1 and res is not None: return jsonify({"status": -5, "msg": "Relation existed"})
        if Bind == 0 and res is None: return jsonify({"status": -6, "msg": "Relation is not existed"})

        # One Device One Room
        if Bind == 1:
            cursor = c.execute("SELECT HID from rHardware where HID = ? and (SELECT Ctrl from Hardware where HID=?) = ?", (HID, HID, 1))
            res = cursor.fetchone()
            if res is not None: return jsonify({"status": -9, "msg": "A device can only bind with one room"})
            cursor = c.execute("SELECT RID, HID from rHardware where RID = ? and HID in (SELECT HID from Hardware where Ctrl = ?) and (SELECT Ctrl from Hardware where HID=?) = ?", (RID, 1, HID, 1))
            res = cursor.fetchone()
            if res is not None: return jsonify({"status": -10, "msg": "A room can only contains one device"})

        if Bind == 1:
            c.execute("INSERT INTO rHardware (HID, RID) VALUES ('%s', %d)" % (str(HID), int(RID)))
        else:
            c.execute("DELETE from rHardware where HID = ? and RID = ?",(HID, RID))

        conn.commit()
        return jsonify({"status": 0})

    if request.method == 'GET': return db_connection("Bind Hardware", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Bind Hardware", request.form.to_dict(), func)

# 查询大楼列表列表
@api.route('/user/building', methods = ['GET', 'POST'])
def user_building():
    def func(c, conn, params):
        cursor = c.execute("SELECT BID, Nickname, Details from Building")

        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append({"BID": res[0], "Nickname": res[1], "Details": res[2]})

        conn.commit()
        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET': return db_connection("Building", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Building", request.form.to_dict(), func)

# 服务器查询房间硬件列表
@api.route('/server/Hardware', methods = ['GET', 'POST'])
def server_hardware():
    def func(c, conn, params):
        RID = params["RID"]
        Ctrl = params["Ctrl"]
        cursor = c.execute("SELECT HID, Nickname, Type, Ctrl FROM Hardware WHERE HID IN (SELECT DISTINCT HID FROM rHardware WHERE RID=?) and Ctrl = ?", (RID, Ctrl))

        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append(res[0])

        conn.commit()
        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET': return db_connection("Hardware", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Hardware", request.form.to_dict(), func)

# 服务器查询房间列表
@api.route('/server/room', methods = ['GET', 'POST'])
def server_room():
    def func(c, conn, params):
        if "HID" in params:
            cursor = c.execute("SELECT DISTINCT RID FROM rHardware WHERE HID = '%s'" % params["HID"])
        else:
            cursor = c.execute("SELECT RID FROM Room")

        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append(res[0])

        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET':
        return db_connection("Room", request.args.to_dict(), func)
    if request.method == 'POST':
        return db_connection("Room", request.form.to_dict(), func)

# 服务器查询硬件
@api.route('/server/hardwareInfo', methods = ['GET', 'POST'])
def server_hardwareInfo():
    def func(c, conn, params):
        cursor = c.execute("SELECT HID, Nickname, Type, Ctrl FROM Hardware WHERE HID = '%s'" % params["HID"])
        res = cursor.fetchone()
        ret = {"hid":res[0], "nickname":res[1], "type" : res[2], "ctrl" : res[3]}
        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET':
        return db_connection("HardwareInfo", request.args.to_dict(), func)
    if request.method == 'POST':
        return db_connection("HardwareInfo", request.form.to_dict(), func)

# 服务器查询用户
@api.route('/server/userInfo', methods = ['GET', 'POST'])
def server_userInfo():
    def func(c, conn, params):
        cursor = c.execute("SELECT UID, Nickname, Authority FROM User WHERE UID = %s" % params["UID"])

        res = cursor.fetchone()
        ret = {"uid": res[0], "nickname": res[1], "authority": res[2]}

        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET':
        return db_connection("User", request.args.to_dict(), func)
    if request.method == 'POST':
        return db_connection("User", request.form.to_dict(), func)


def main():
    # Init DB
    if not os.path.isfile(PATH):
        DBInit.create_building_table();
        DBInit.create_user_table()
        DBInit.create_room_table()
        DBInit.create_hardware_table()
        DBInit.create_rHardware_table()
        DBInit.create_rUser_table()

    # Init Server
    api.run(host='0.0.0.0', port=50001, threaded=True)




if __name__=="__main__": main()