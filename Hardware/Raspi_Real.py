import time
import json
import RPi.GPIO as GPIO
from urllib import parse, request
import configparser

CONFIG_FILE = "config.ini"
SERVER_ADDR = "http://192.168.8.110:443/hardware"


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
    conf.set("Port", "Camera", str(False))
    conf.set("Port", "I2C", str(False))

    if not conf.has_section("Actuator"): conf.add_section("Actuator")
    for i in range(0, 40): conf.set("Actuator", str(i), str(True))
    conf.set("Actuator", "Camera", str(False))
    conf.set("Actuator", "I2C", str(False))

    if not conf.has_section("Default"): conf.add_section("Default")
    for i in range(0, 40): conf.set("Default", str(i), str(0))
    conf.write(open(CONFIG_FILE, "w"))


def setup_sensor(i):
    if i == "Camera": return
    if i == "I2C": return
    GPIO.setup(int(i), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def setup_actuator(i, defa):
    GPIO.setup(int(i), GPIO.OUT)
    GPIO.output(int(i), GPIO.LOW if int(defa)==0 else GPIO.HIGH)


def get_sensor(i):
    if i == "Camera": return 0
    if i == "I2C": return 0
    return GPIO.input(int(i))


def set_actuator(i, v):
    GPIO.output(int(i),  GPIO.LOW if int(v)==0 else GPIO.HIGH)


def main():
    global CONFIG_FILE, SERVER_ADDR
    conf = configparser.ConfigParser()
    conf.read(CONFIG_FILE)

    if not conf.has_section("Config"): init_config(conf)
    uid = conf.get("Config", "uid")
    print(" * Raspi : Read Uid " + uid)

    # Init GPIO
    GPIO.setmode(GPIO.BCM)
    for i in range(0, 40):
        if not conf.getboolean("Port", str(i)): continue
        if conf.getboolean("Actuator", str(i)):
            setup_actuator(i, conf.getint("Default", str(i)))
        else:
            setup_sensor(i)


    while True:
        try:
            content = {"0": {}, "1":{}, "2": {}}

            # Generate Sensors Data
            gpioList = range(40)
            gpioList.append("Camera")
            gpioList.append("I2C")
            for p in gpioList:
                if not conf.getboolean("Port", str(p)): continue
                if conf.getboolean("Actuator", str(p)): continue
                print("Get GPIO " + str(p) + "=" + str(get_sensor(p)))
                content["0"][str(p)] = get_sensor(p)

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

            # Swith to Sensor
            for p in content["0"]:
                if not conf.getboolean("Port", str(p)) or conf.getboolean("Actuator", str(p)):
                    # Set Port
                    setup_sensor(p)
                    print("Set GPIO.IN " + str(p))

                conf.set("Actuator", str(p), str(False))
                conf.set("Port", str(p), str(True))

            # Switch to Actuator and Setting
            for p in content["1"]:
                if not conf.getboolean("Port", str(p)) or not conf.getboolean("Actuator", str(p)):
                    # Set Port
                    setup_actuator(p, content["2"][str(p)])
                    print("Set GPIO.OUT " + str(p))

                conf.set("Actuator", str(p), str(True))
                conf.set("Port", str(p), str(True))
                conf.set("Default", str(p), str(content["2"][str(p)]))

                set_actuator(p, content["1"][str(p)])
                print("Set GPIO " + str(p) + " " + str(content["1"][str(p)]))

            # Write to Config
            conf.write(open(CONFIG_FILE, "w"))

        except Exception as err:
            print(err)
        time.sleep(5)

if __name__ == "__main__":
    main()