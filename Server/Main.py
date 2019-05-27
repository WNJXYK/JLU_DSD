import sys
sys.path.append(sys.path[0] + "/..")

from flask_cors import CORS
from flask import Flask
from Server.Database import IDatabase
from Server.Controller import IController
from Server import Config



from threading import Thread
import time

app = Flask(__name__)
CORS(app)

@app.errorhandler(404)
def page_not_found(e):
    return "Opsss. This is a private page."


def API():
    from Server.API import Hardware
    from Server.API import Interface
    from Server.API import Command
    from Server.API import Open
    from Server.API import Controller
    from Server.API import Debug
    app.register_blueprint(Hardware.api, url_prefix="/hardware")
    app.register_blueprint(Interface.api, url_prefix="/interface")
    app.register_blueprint(Command.api, url_prefix="/command")
    app.register_blueprint(Open.api, url_prefix="/open")
    app.register_blueprint(Controller.api, url_prefix="/control")
    app.register_blueprint(Debug.api, url_prefix="/debug")
    app.run(host='0.0.0.0', port=443, threaded=True, debug=True)


def Heartbeat():
    def func():
        while True:
            IController.heart_beat()
            time.sleep(Config.HEART_BEAT)
    thread = Thread(target=func)
    thread.setDaemon(True)
    thread.start()


def main():
    IDatabase.install()
    Heartbeat()
    API()


if __name__ == '__main__':
    main()