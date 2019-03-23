import time, json
from Demo.Database import Database



class Hardware(object):
    '''
    服务器硬件类：负责更新、存储传感器的数据，并需要的时候进行数据打包。
    Hardware Class: Aim for updating, saving and sensors's and devices's data And packing them when needed.
    '''

    def __init__(self, manager):
        self.data = manager.dict()
        # self.database = db

    def init(self, hid):
        if hid not in self.data:
            self.data[hid] = {
                "online": 0,
                "type": "???",
                "data": "offline",
                "last": time.time()
            }

    def modify(self, hid, key, value):
        info = self.data[hid]
        info[key] = value
        self.data[hid] = info

    def get(self, hid):
        self.init(hid)
        return self.data[hid]


    def online(self, hid, type):
        self.init(hid)
        self.modify(hid, "online", 1)
        self.modify(hid, "type", type)
        self.modify(hid, "data", "Waiting")
        self.modify(hid, "last", time.time())

    def offline(self, hid):
        self.modify(hid, "online", 0)
        self.modify(hid, "data", "offline")
        self.modify(hid, "last", time.time())

    def report(self, hid, data):
        self.modify(hid, "data", json.loads(data)[data])
        self.modify(hid, "last", time.time())


    def query(self, hid):
        info = Database.get_hardwareInfo(hid)
        ret = {
            "id": hid,
            "nickname": info["nickname"]
        }
        info = self.get(hid)
        ret["online"] = info["online"]
        if info["online"] == 1:
            ret["data"] = info["data"]
            ret["type"] = info["type"]
            ret["last"] = info["last"]
        return ret