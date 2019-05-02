import time, json
# from Demo.Database import Database


class Hardware(object):
    '''
    服务器硬件类：负责更新、存储传感器的数据，并需要的时候进行数据打包。
    Hardware Class: Aim for updating, saving and sensors's and devices's data And packing them when needed.
    '''

    def __init__(self, manager, idb, heartbeat = 10):
        '''
        构造函数 / Construct function
        :param manager: 为了创建线程安全变量 / For creating thread-safe variable
        '''
        self.data = manager.dict()
        self.db = idb
        self.heartbeat = heartbeat

    def init(self, hid):
        '''
        初始化硬件数据 / Init hardware data
        :param hid:  硬件ID / Hardware ID
        :return:
        '''
        if hid not in self.data:
            info = self.db.getHardware(hid)
            self.data[hid] = {
                "hid": hid,
                "online": 0,
                "type": info["type"],
                "data": "offline",
                "last": 0.0
            }

    def verify_online(self, hid):
        '''
        使用心跳包检测硬件是否在线
        Verify online state with heartbeat package
        :param hid: 硬件ID / Hardware ID
        '''
        if self.heartbeat < 0: return
        self.init(hid)
        info = self.data[hid]
        if info["online"] == 1 and time.time()-info["last"] > self.heartbeat:
            print("Reporter : %s(%s) is lost" % (info["type"], hid))
            self.modify(hid, "online", 0)
        if info["online"] == 0 and time.time()-info["last"] < self.heartbeat:
            print("Reporter : %s(%s) is back" % (info["type"], hid))
            self.modify(hid, "online", 1)

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
        self.verify_online(hid)
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
        msg = json.loads(raw)

        # 硬件数据 / Hardware data
        if "data" in msg:
            self.modify(hid, "data", msg["data"])

        # 硬件上一条指令 / hardware's last command
        if "cmd" in msg:
            self.modify(hid, "cmd", msg["cmd"])

        self.modify(hid, "last", time.time())

    def query(self, hid):
        '''
        查询硬件信息 / Query hardware info
        :param hid: 硬件ID / Hardware ID
        :return: 硬件信息 / Hardware info
        '''
        info = self.db.getHardware(hid)
        ret = {
            "id": hid,
            "nickname": info["nickname"],
            "type": info["type"]
        }
        info = self.get(hid)
        ret["online"] = info["online"]
        if info["online"] == 1:
            ret["data"] = info["data"]
            # ret["type"] = info["type"]
            ret["last"] = info["last"]

        return ret
