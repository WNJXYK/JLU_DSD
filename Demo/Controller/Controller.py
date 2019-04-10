import json
class Controller(object):
    def __init__(self):
        self.last = {}
        self.BeatLimit = 30
        self.CtrlLimit = 10

    def Init(self):
        pass

    def getSensorData(self, list):
        tot = {}
        cnt = {}
        for item in list:
            if item["online"]==0: continue
            if item["type"] not in tot:
                tot[item["type"]] = 1
                cnt[item["type"]] = 0
            else:
                tot[item["type"]] = tot[item["type"]] + 1

            # Merge Sensors
            if item["type"]=="CameraSensor" :
                if item["data"] == "True": cnt[item["type"]] = cnt[item["type"]] + 1
            if item["type"]=="LightSensor" :
                if float(item["data"]) > 0.5: cnt[item["type"]] = cnt[item["type"]] + 1

        ret = []
        for key in tot:
            ret.append(cnt[key]*2>tot[key])

        return ret

    def Beat(self, info):
        ret = {}
        return json.dumps(ret)

    def Run(self, info):
        ret = {}
        if len(info["sensors"]) <= 0: return json.dumps(ret)
        if len(info["device"]) <= 0: return json.dumps(ret)
        device = info["device"][0]
        if device["online"] == 0: return json.dumps(ret)

        rid, now = info["rid"], info["time"]

        if rid in self.last and (now - self.last[rid] <= self.BeatLimit): return json.dumps(ret)

        sensors = self.getSensorData(info["sensors"])

        print(sensors, map((lambda x, y: x or y), sensors))

        if len(sensors) < 0 or map((lambda x, y: x or y), sensors)==False: ret["data"] = "off"

        return json.dumps(ret)

    def Cmd(self, info):
        print(info)
        ret = {}
        if len(info["device"]) <= 0: return json.dumps(ret), False, "No device."
        device = info["device"][0]
        if device["online"] == 0: return json.dumps(ret), False, "Device is not online."

        rid, now = info["rid"], info["time"]
        print(rid, now)
        auth = 0
        if "cmd" in device and "authority" in device["cmd"]:
            print(device["cmd"])
            cmd = json.loads(device["cmd"])
            auth = cmd["authority"]
        print(auth)

        user = info["user"]
        if rid in self.last and (now - self.last[rid] <= self.CtrlLimit):
            if user["authority"] < auth:
                return json.dumps(ret), False, "Invalid Authority"
        print(info["cmd"])
        self.last[rid] = now
        ret["data"] = info["cmd"]
        ret["authority"] = user["authority"]

        return json.dumps(ret), True, "Message Sent"
