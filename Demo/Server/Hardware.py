import time, json
from Demo.Database import Database


class Hardware(object):
    '''
    服务器硬件类：负责更新、存储传感器的数据，并需要的时候进行数据打包。
    Hardware Class: Aim for updating, saving and sensors's and devices's data And packing them when needed.
    '''

    def __init__(self, manager):
        '''
        构造函数 / Construct function
        :param manager: 为了创建线程安全变量 / For creating thread-safe variable
        '''
        self.data = manager.dict()

    def init(self, hid):
        '''
        初始化硬件数据 / Init hardware data
        :param hid:  硬件ID / Hardware ID
        :return:
        '''
        if hid not in self.data:
            self.data[hid] = {
                "online": 0,
                "type": "???",
                "data": "offline",
                "last": time.time()
            }

    def modify(self, hid, key, value):
        '''
        修改硬件数据 / Modify hardware data
        :param hid: 硬件ID / Hardware ID
        :param key: 参数名称 / Parameter names
        :param value: 数据 / Data
        '''
        info = self.data[hid]
        info[key] = value
        self.data[hid] = info

    def get(self, hid):
        '''
        获得硬件数据 / Get hardware data
        :param hid: 硬件ID / Hardware ID
        :return: 硬件数据 / Hardware data
        '''
        self.init(hid)
        return self.data[hid]

    def online(self, hid, typ):
        '''
        设置硬件在线 / Set hardware online
        :param hid: 硬件ID / Hardware ID
        :param typ: 硬件类型 / Hardware type
        '''
        self.init(hid)
        self.modify(hid, "online", 1)
        self.modify(hid, "type", typ)
        self.modify(hid, "data", "Waiting")
        self.modify(hid, "last", time.time())

    def offline(self, hid):
        '''
        设置硬件离线 / Set hardware offline
        :param hid: 硬件ID / Hardware ID
        '''
        self.modify(hid, "online", 0)
        self.modify(hid, "data", "offline")
        self.modify(hid, "last", time.time())

    def report(self, hid, raw):
        '''
        更新硬件数据 / Update hardware data
        :param hid: 硬件ID / Hardware ID
        :param raw: 原数据 / Raw data
        '''
        self.modify(hid, "data", json.loads(raw)["data"])
        self.modify(hid, "last", time.time())

    def query(self, hid):
        '''
        查询硬件信息 / Query hardware info
        :param hid: 硬件ID / Hardware ID
        :return: 硬件信息 / Hardware info
        '''
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
