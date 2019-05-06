import os, sys, getopt
import traceback
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

import hashlib, sqlite3, time
from flask import Flask, request, jsonify
from flask_cors import *
from Simulate.Database import DBInit


# API Service
api = Flask(__name__)
CORS(api)

# 用户登陆
@api.route('/api', methods = ['POST'])
def user_login():
    data = request.form.to_dict()
    print(data)
    return jsonify({"msg": "{}", "flag":0, "message":""})



def main():
    # Init Server
    api.run(host='0.0.0.0', port=50002, threaded=True)



if __name__=="__main__": main()