import json
class Controller(object):
    def __init__(self):
        pass

    def Init(self):
        pass

    def getSensorData(self, list):
        tot = {}
        cnt = {}
        for item in list:
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
        print(info)
        ret = {}
        if len(info["sensors"]) <= 0: return json.dumps(ret)
        if len(info["device"]) <= 0: return json.dumps(ret)

        sensors = info["sensors"][0]
        if ('data' in sensors) and (sensors["data"] == 'True'): return '{"data":"on"}'
        return '{"data":"off"}'

    def Run(self, info):
        print(info)
        if len(info["sensors"]) <= 0: return json.dumps({})
        sensors = info["sensors"][0]
        if ('data' in sensors) and (sensors["data"] == 'True'): return '{"data":"on"}'
        return '{"data":"off"}'

    def Cmd(self, info):
        print(info)
        return '{"data":"%s"}'%info["cmd"]
