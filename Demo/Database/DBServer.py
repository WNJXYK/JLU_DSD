import os, sys, getopt
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

import hashlib, sqlite3, time
from flask import Flask, request, jsonify
from flask_cors import *

# Constant
PATH = "./database.db"

# API Service
api = Flask(__name__)
CORS(api)


@api.route('/api/user/login', methods = ['GET'])
def user_login():
    try:
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        email = request.args.get('email')
        password = request.args.get('password')
        print("Login", email, password)

        cursor = c.execute("SELECT UID, Authority from User where Email=? and Password=?", (email, password))
        res = cursor.fetchone()

        if res is None:
            return jsonify({"status":-1, "msg":"Incorrect Email or Password"})

        UID = res[0]
        Authority = res[1]
        SID = md5(str(time.time()))

        c.execute("UPDATE User SET SID = '%s' WHERE UID = %d" % (SID, UID))
        conn.commit()

        return jsonify({"status": 0, "msg": "Login", "info": {"UID": UID, "SID": SID, "Authority": Authority}})

    except Exception as err:
        print("Login", err)
        return jsonify({"status": -2, "msg": "Server Error"})

    finally:
        c.close()
        conn.close()


@api.route('/api/user/verify', methods = ['GET'])
def user_verify():
    try:
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        UID = request.args.get('UID')
        SID = request.args.get('SID')
        print("Verify", UID, SID)

        cursor = c.execute("SELECT UID, Authority from User where SID=? and UID=?", (SID, UID))
        res = cursor.fetchone()

        if res is None:
            return jsonify({"status":-1, "msg":"Invalid User"})

        UID = res[0]
        Authority = res[1]

        return jsonify({"status": 0, "msg": "Valid User", "info": {"UID": UID, "Authority": Authority}})

    except Exception as err:
        print("Verify", err)
        return jsonify({"status": -2, "msg": "Server Error"})

    finally:
        c.close()
        conn.close()


# Database
global conn
conn = None

def md5(s):
    ret = hashlib.md5()
    ret.update(s.encode("utf8"))
    return ret.hexdigest()


def create():
    global conn, PATH
    conn = sqlite3.connect(PATH)

    # Create User Table
    c = conn.cursor()
    c.execute('''CREATE TABLE User
           (UID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           Nickname TEXT NOT NULL,
           Password TEXT NOT NULL,
           Email TEXT NOT NULL,
           SID TEXT,
           Authority INT NOT NULL);
           ''')
    c.execute("INSERT INTO User (Nickname, Password, Email, SID, Authority) \
            VALUES ('Administrator', '%s', 'wnjxyk@gmail.com', '%s', 4)" % (md5("admin"), md5(str(time.time()))))
    conn.commit()

    conn.close()


def main():
    print(md5("admin"))

    global PATH, conn
    try:
        if not os.path.isfile(PATH): create()

        # Init Server
        api.run(host='0.0.0.0', port=50004, threaded=True)
    finally: conn.close()



if __name__=="__main__": main()