import time
import json
from urllib import parse, request
import configparser

CONFIG_FILE = "config.ini"
SERVER_ADDR = "http://0.0.0.0:8088/hardware"


def post(url, data):
    data = parse.urlencode(data).encode(encoding='utf-8')
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                   "Content-Type": "application/x-www-form-urlencoded"}
    req = request.Request(url=url, data=data, headers=header_dict)
    res = request.urlopen(req)
    res = res.read().decode("utf-8")
    return res


def allocate_uid():
    global SERVER_ADDR
    url = SERVER_ADDR + "/allocate"
    while True:
        obj = json.loads(post(url, {}))
        if obj['status'] == 0: return obj['info']
        time.sleep(5)


def init_config(conf):
    global CONFIG_FILE
    if not conf.has_section("Config"): conf.add_section("Config")
    conf.set("Config", "uid", allocate_uid())
    print(" * Raspi : Allocated Uid " + conf.get("Config", "uid"))
    if not conf.has_section("Port"): conf.add_section("Port")
    for i in range(0, 40): conf.set("Port", str(i), str(False))
    if not conf.has_section("Actuator"): conf.add_section("Actuator")
    for i in range(0, 40): conf.set("Actuator", str(i), str(True))
    if not conf.has_section("Default"): conf.add_section("Default")
    for i in range(0, 40): conf.set("Default", str(i), str(0))
    conf.write(open(CONFIG_FILE, "w"))


def main():
    global CONFIG_FILE, SERVER_ADDR
    conf = configparser.ConfigParser()
    conf.read(CONFIG_FILE)


    if not conf.has_section("Config"): init_config(conf)
    uid = conf.get("Config", "uid")
    print(" * Raspi : Read Uid " + uid)

    while True:
        content = {"0": {}, "1":{}, "2": {}}

        # Make Sensors Data
        for p in range(40):
            if not conf.getboolean("Port", str(p)): continue
            if conf.getboolean("Actuator", str(p)): continue
            print("Get GPIO " + str(p))
            content["0"][str(p)] = 1 if p == 3 else 0

        # Report to Server
        url = SERVER_ADDR + "/report"
        res = post(url, {"uid":uid, "content":json.dumps(content)})
        obj = json.loads(res)

        # Delete By Server
        status = int(obj["status"])
        if status != 0:
            init_config(conf)
            uid = conf.get("Config", "uid")
            continue

        # Solve Input / Output / Default Setting
        content = obj["info"]
        for p in range(40):
            if (str(p) not in content["0"]) and (str(p) not in content["1"]):
                conf.set("Port", str(p), str(False))

        print(content)
        for p in content["0"]:

            if not conf.getboolean("Port", str(p)) or conf.getboolean("Actuator", str(p)):
                # Set Port
                print("Set " + str(p))

            conf.set("Actuator", str(p), str(False))
            conf.set("Port", str(p), str(True))

        for p in content["1"]:
            if not conf.getboolean("Port", str(p)) or not conf.getboolean("Actuator", str(p)):
                # Set Port
                print("Set " + str(p))

            conf.set("Actuator", str(p), str(True))
            conf.set("Port", str(p), str(True))
            conf.set("Default", str(p), str(content["2"][str(p)]))
            print("Set GPIO " + str(p) + " " + str(content["1"][str(p)]))

        conf.write(open(CONFIG_FILE, "w"))
        time.sleep(5)

if __name__ == "__main__":
    main()