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
        return func(c, params)
    except Exception as err:
        print(name, err)
        return jsonify({"status": -2, "msg": "Server Error"})
    finally:
        c.close()
        conn.close()

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

@api.route('/user/room', methods = ['GET', 'POST'])
def user_room():
    def func(c, params):
        if ("SID" not in params) or ("UID" not in params): return jsonify({"status": -1, "msg": "Invalid Request"})
        SID, UID = params["SID"], params["UID"]

        cursor = c.execute("SELECT Authority from User where SID=? and UID=?", (SID, UID))
        res = cursor.fetchone()
        if res is None: return jsonify({"status":-3, "msg":"Invalid User"})
        Authority = res[0]

        if Authority >= 3:
            cursor = c.execute("SELECT RID, Nickname, SensorCNT, DeviceCNT, Details FROM Room")
        else:
            cursor = c.execute("SELECT RID, Nickname, SensorCNT, DeviceCNT, Details FROM Room \
                               WHERE RID IN (SELECT DISTINCT RID FROM rUser WHERE UID = ?)", (UID))
        ret = []
        while True:
            res = cursor.fetchone()
            if res is None: break
            ret.append({"RID": res[0], "Nickname": res[1], "sCNT": res[2], "dCNT": res[3], "Details": res[4]})

        return jsonify({"status": 0, "info": ret})

    if request.method == 'GET':
        return db_connection("Room", request.args.to_dict(), func)
    if request.method == 'POST':
        return db_connection("Room", request.form.to_dict(), func)

def main():
    print(DBInit.md5("admin"))

    global PATH, conn
    try:
        if not os.path.isfile(PATH):
            DBInit.create_user_table()
            DBInit.create_room_table()
            DBInit.create_hardware_table()
            DBInit.create_rHardware_table()
            DBInit.create_rUser_table()

        # Init Server
        api.run(host='0.0.0.0', port=50001, threaded=True)
    finally: conn.close()



if __name__=="__main__": main()