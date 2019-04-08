import os, sys, getopt
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

import hashlib, sqlite3, time
from flask import Flask, request, jsonify
from flask_cors import *
from Demo.Database import DBInit

# Constant
PATH = "./database.db"

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

        print("Verify", UID, SID)

        cursor = c.execute("SELECT UID, Authority, Nickname from User where SID=? and UID=?", (SID, UID))
        res = cursor.fetchone()

        if res is None: return jsonify({"status":-3, "msg":"Invalid User"})

        UID, Authority, Nickname = res[0], res[1], res[2]
        return jsonify({"status": 0, "msg": "Valid User", "info": {"UID": UID, "Authority": Authority, "Nickname": Nickname}})

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
        Offset, Delta = 0, 10
        if "Offset" in params: Offset = params["Offset"]
        if "Delta" in params: Delta = params["Delta"]

        cursor = c.execute("SELECT Authority from User where SID=? and UID=?", (SID, UID))
        res = cursor.fetchone()
        if res is None: return jsonify({"status":-3, "msg":"Invalid User"})
        Authority = res[0]

        cnt = 0
        if Authority >= 3:
            cursor = c.execute("SELECT COUNT(*) FROM Room")
        else:
            cursor = c.execute("SELECT COUNT(*) FROM Room \
                               WHERE RID IN (SELECT DISTINCT RID FROM rUser WHERE UID = ?)", (UID))
        cnt = cursor.fetchone()[0]

        if Authority >= 3:
            cursor = c.execute("SELECT RID, Nickname, SensorCNT, DeviceCNT, Details FROM Room LIMIT ? OFFSET ?", (Delta, Offset))
        else:
            cursor = c.execute("SELECT RID, Nickname, SensorCNT, DeviceCNT, Details FROM Room \
                               WHERE RID IN (SELECT DISTINCT RID FROM rUser WHERE UID = ?) LIMIT ? OFFSET ?", (UID, Delta, Offset))
        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append({"RID": res[0], "Nickname": res[1], "sCNT": res[2], "dCNT": res[3], "Details": res[4]})

        auth = 0
        if Authority >= 3: auth = 1

        return jsonify({"status": 0, "info": {"arr":ret, "cnt":cnt, "allow": auth}})

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
        Delete, Details = 0, None
        if "Delete" in params: Delete = int(params["Delete"])
        if "Details" in params: Details = params["Details"]
        print(Details, Delete)

        cursor = c.execute("SELECT Authority from User where SID=? and UID=?", (SID, UID))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < 3: return jsonify({"status": -4, "msg": "Invalid Authority"})

        if Delete == 1:
            c.execute("DELETE from Room where RID=?", (RID))
            c.execute("DELETE from rUser where RID=?", (RID))
            c.execute("DELETE from rHardware where RID=?", (RID))
            conn.commit()
        elif Details is not None:
            c.execute("UPDATE Room set Details = ? where RID=?", (Details, RID))
            conn.commit()
        return jsonify({"status": 0, "info": conn.total_changes})

    if request.method == 'GET': return db_connection("Modify_Room", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Modify_Room", request.form.to_dict(), func)

# 增加房间
@api.route('/user/add_room', methods = ['GET', 'POST'])
def user_add_room():
    def func(c, conn, params):
        if ("SID" not in params) or ("UID" not in params) or ("Nickname" not in params) or ("Details" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID, Nickname, Details = params["SID"], params["UID"], params["Nickname"], params["Details"]

        cursor = c.execute("SELECT Authority from User where SID=? and UID=?", (SID, UID))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < 3: return jsonify({"status": -4, "msg": "Invalid Authority"})

        sql = "INSERT INTO Room (Nickname, SensorCNT, DeviceCNT, Details) VALUES ('%s', 0, 0, '%s')" %(str(Nickname), str(Details))
        print(sql)
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

        cursor = c.execute("SELECT Authority from User where SID=? and UID=?", (SID, UID))
        res = cursor.fetchone()
        if res is None: return jsonify({"status": -3, "msg": "Invalid User"})
        if res[0] < 3:
            cursor = c.execute("SELECT * rUser from User where UID=? and RID=?", (UID, RID))
            res = cursor.fetchone()
            if res is None: return jsonify({"status": -4, "msg": "Invalid Authority"})

        cursor = c.execute("SELECT HID, Nickname, Type, Ctrl FROM Hardware\
                  WHERE HID IN (SELECT HID FROM rHardware WHERE RID=?)", (RID))

        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append({"HID": res[0], "Nickname": res[1], "Type": res[2], "Ctrl": res[3]})

        conn.commit()
        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET': return db_connection("Hardware", request.args.to_dict(), func)
    if request.method == 'POST': return db_connection("Hardware", request.form.to_dict(), func)


def main():
    # Init DB
    if not os.path.isfile(PATH):
        DBInit.create_user_table()
        DBInit.create_room_table()
        DBInit.create_hardware_table()
        DBInit.create_rHardware_table()
        DBInit.create_rUser_table()

    # Init Server
    api.run(host='0.0.0.0', port=50001, threaded=True)




if __name__=="__main__": main()