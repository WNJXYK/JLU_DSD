import json, urllib
import Config

class IDatabase(object):

    def __init__(self):
        self.DBS = Config.DBServer

    def post(self, url, data):
        data = urllib.parse.urlencode(data).encode(encoding='utf-8')
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko', "Content-Type": "application/x-www-form-urlencoded"}
        req = urllib.request.Request(url=url, data=data, headers=header_dict)
        res = urllib.request.urlopen(req)
        res = res.read().decode("utf-8")
        return res

    def getSensorHID(self, RID):
        res = self.post(self.DBS + "/server_Sensor", RID)
        obj = json.loads(res)
        if obj["status"] != 0: return []

        return obj["info"]

    def getDeviceHID(self, RID):
        res = self.post(self.DBS + "/server_Device", RID)
        obj = json.loads(res)
        if obj["status"] != 0: return []

        return obj["info"]

    def getAllRoomRID(self):
        res = self.post(self.DBS+"/server_room",{"HID":"0"})
        obj = json.loads(res)
        if obj["status"]!=0: return []
        # ret = [str(x) for x in obj["info"]]

        return obj["info"]

    def getRoomRID(self, HID):
        res = self.post(self.DBS+"/server_room",{"HID" : HID})
        obj = json.loads(res)
        if obj["status"]!=0: return []

        return obj["info"]

    def getHardware(self, HID):


        res = self.post(self.DBS + "/server_hardwareInfo", {"HID": HID})
        obj = json.loads(res)
        if obj["status"] == 0:
            hid = obj["HID"]
            typ = obj["type"]
            ret = {"hid": hid, "type":typ, "ctrl":0}

            return ret

        res = self.post(self.DBS + "/server_deviceInfo", {"LID": HID})
        obj = json.loads(res)
        if obj["status"] == 0:
            hid = obj["LID"]
            ret = {"hid": hid, "type": 0, "ctrl": 1}

            return ret

        return {}


    def isHardware(self, HID):
        info = self.getHardware(HID)

        return "hid" in info
        # return True

    def isDevice(self, HID):
        info = self.getHardware(HID)

        if not "hid" in info: return False
        return info["ctrl"] == 1
        # return True

    def getUser(self, UID):
        res = self.post(self.DBS + "/server_userInfo", {"UID": UID})
        obj = json.loads(res)
        if obj["status"] != 0: return []

        return obj["info"]

    def checkUserHardware(self, UID, SID, HID): return True

