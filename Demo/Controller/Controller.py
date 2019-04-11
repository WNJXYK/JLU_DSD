import json
class Controller(object):
    # 教师开灯持久化
    # 高等级开灯低等级短时间内无法重写
    # 低等级开灯，自动关闭
    def __init__(self):
        self.last = {}
        self.RunLimit = 60
        self.CtrlLimit = 30
        self.AutoLimit = 2

    def Init(self):
        pass

    def getSensorData(self, list):
        tot = {}
        cnt = {}
        button_flag = False

        for item in list:
            if item["online"]==0: continue
            if item["type"] not in tot:
                tot[item["type"]] = 1
                cnt[item["type"]] = 0
            else:
                tot[item["type"]] = tot[item["type"]] + 1

            # Merge Sensors
            if item["type"] == "PresenceSensor":
                if item["data"] == "True": cnt[item["type"]] = cnt[item["type"]] + 1
            if item["type"] == "LightSensor":
                if float(item["data"]) > 0.5: cnt[item["type"]] = cnt[item["type"]] + 1
            if item["type"] == "ButtonSensor":
                if item["data"] == "True": cnt[item["type"]] = cnt[item["type"]] + 1

        if "ButtonSensor" in tot and cnt["ButtonSensor"]>0: button_flag = True
        ret = []
        for key in tot:
            if key == "ButtonSensor": continue
            ret.append(cnt[key]*2>tot[key])

        return ret, button_flag

    def Beat(self, info):
        return self.Run(info, False)

    def Run(self, info, flag = True):
        ret = {}

        # No Need to do anything
        if len(info["sensors"]) <= 0: return json.dumps(ret)
        if len(info["device"]) <= 0: return json.dumps(ret)
        device = info["device"][0]
        if device["online"] == 0: return json.dumps(ret)

        rid, now = info["rid"], info["time"]
        sensors, button = self.getSensorData(info["sensors"])
        # print(sensors, button)

        # Solve Button
        if flag and button:
            self.last[rid] = now
            ret["data"] = "off" if device["data"]=="True" else "on"
            ret["authority"] = self.AutoLimit + 1
            return json.dumps(ret)

        # No Need to do anything
        if device["data"] == "False": return json.dumps(ret)

        # print(rid, now - self.last[rid])

        # Auto Close
        if rid in self.last and (now - self.last[rid] <= self.RunLimit): return json.dumps(ret)
        if "cmd" in device and "authority" in device["cmd"]:
            cmd = json.loads(device["cmd"])
            # print(cmd["authority"])
            if cmd["authority"] > self.AutoLimit: return json.dumps(ret)

        v = False
        for x in sensors: v = v or x

        if len(sensors) <= 0 or (v == False): ret["data"] = "off"
        # print(v, ret)

        return json.dumps(ret)

    def Cmd(self, info):
        # print(info)
        ret = {}
        if len(info["device"]) <= 0: return json.dumps(ret), False, "No device."
        device = info["device"][0]
        if device["online"] == 0: return json.dumps(ret), False, "Device is not online."

        rid, now = info["rid"], info["time"]
        # print(rid, now)
        auth = 0
        if "cmd" in device and "authority" in device["cmd"]:
            # print(device["cmd"])
            cmd = json.loads(device["cmd"])
            auth = cmd["authority"]
        # print(auth)

        user = info["user"]
        if rid in self.last and (now - self.last[rid] <= self.CtrlLimit):
            if user["authority"] < auth:
                return json.dumps(ret), False, "Invalid Authority"
        # print(info["cmd"])
        self.last[rid] = now
        ret["data"] = info["cmd"]
        ret["authority"] = user["authority"]

        return json.dumps(ret), True, "Message Sent"
