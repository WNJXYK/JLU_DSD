import time
import json
import RPi.GPIO as GPIO
from urllib import parse, request
import configparser

# Interface With Server
class Interface:
    def __init__(self):
        self.CONFIG_FILE = "/home/pi/DSD_config.ini"
        self.SERVER_ADDR = "http://39.106.7.29:8088/hardware"
        self.NAME = "Raspi"
        
        self.conf = configparser.ConfigParser()
        self.conf.read(self.CONFIG_FILE)

        if not self.conf.has_section("Config"):
            self.init_config()
        else:
            self.uid = self.conf.get("Config", "uid")
            print(" * Raspi : Read Uid " + self.uid)

    @staticmethod
    def post(url, data):
        data = parse.urlencode(data).encode(encoding='utf-8')
        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                       "Content-Type": "application/x-www-form-urlencoded"}
        req = request.Request(url=url, data=data, headers=header_dict)
        res = request.urlopen(req)
        res = res.read().decode("utf-8")
        return res

    def request(self, content):
        url = self.SERVER_ADDR + "/report"
        res = Interface.post(url, {"uid": self.uid, "content": json.dumps(content)})
        return json.loads(res)

    def allocate_uid(self):
        url = self.SERVER_ADDR + "/allocate"
        while True:
            obj = json.loads(Interface.post(url, {"name": self.NAME}))
            if obj['status'] == 0: return obj['info']
            time.sleep(5)

    def init_config(self):
        if not self.conf.has_section("Config"): self.conf.add_section("Config")

        self.uid = self.allocate_uid()
        self.conf.set("Config", "uid", self.uid)

        with open(self.CONFIG_FILE, "w") as fp:
            self.conf.write(fp)

        print(" * Raspi : Allocated Uid " + self.uid)

# Mem for Settings
class Memory:
    def __init__(self):
        self.mem = {}

    def clear(self):
        self.mem = {}

    def get_boolean(self, a, b):
        if a not in self.mem: self.mem[a] = {}
        if b not in self.mem[a]: self.mem[a][b] = False
        return self.mem[a][b]

    def get_int(self, a, b):
        if a not in self.mem: self.mem[a] = {}
        if b not in self.mem[a]: self.mem[a][b] = 0
        return self.mem[a][b]

    def set_boolean(self, a, b, c):
        if a not in self.mem: self.mem[a] = {}
        if b not in self.mem[a]: self.mem[a][b] = False
        self.mem[a][b] = c

    def set_int(self, a, b, c):
        if a not in self.mem: self.mem[a] = {}
        if b not in self.mem[a]: self.mem[a][b] = 0
        self.mem[a][b] = c


# Tools for GPIO (And Camera | I2C)
class Tools:
    def __init__(self):
        pass

    @staticmethod
    def setup():
        GPIO.setmode(GPIO.BCM)

    @staticmethod
    def setup_sensor(i):
        if i == "Camera": return
        if i == "I2C": return
        GPIO.setup(int(i), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("Set GPIO.OUT " + str(i))

    @staticmethod
    def setup_actuator(i, defa):
        GPIO.setup(int(i), GPIO.OUT)
        GPIO.output(int(i), GPIO.LOW if int(defa)==0 else GPIO.HIGH)
        print("Set GPIO.IN " + str(i))

    @staticmethod
    def get_sensor(i):
        if i == "Camera": return 0
        if i == "I2C": return 1
        return GPIO.input(int(i))

    @staticmethod
    def set_actuator(i, v):
        GPIO.output(int(i),  GPIO.LOW if int(v)==0 else GPIO.HIGH)


def main():
    # Init
    mem = Memory()
    interface = Interface()
    Tools.setup()

    while True:
        try:
            content = {"0": {}, "1":{}, "2": {}}
            gpio_list = list(range(40))
            gpio_list.append("Camera")
            gpio_list.append("I2C")

            # Generate Sensors Data & Report to Server
            for p in gpio_list:
                if not mem.get_boolean("Port", str(p)): continue
                if mem.get_boolean("Actuator", str(p)): continue
                content["0"][str(p)] = Tools.get_sensor(p)

            obj = interface.request(content)

            # Delete By Server
            status = int(obj["status"])
            if status != 0:
                interface.init_config()
                mem.clear()
                continue

            # Close Nouse Port
            content = obj["info"]
            for p in gpio_list:
                if (str(p) not in content["0"]) and (str(p) not in content["1"]):
                    mem.set_boolean("Port", str(p), False)

            # Swith to Sensor
            for p in content["0"]:
                if not mem.get_boolean("Port", str(p)) or mem.get_boolean("Actuator", str(p)):
                    Tools.setup_sensor(p)

                mem.set_boolean("Actuator", str(p), False)
                mem.set_boolean("Port", str(p), True)

            # Switch to Actuator and Setting
            for p in content["1"]:
                if not mem.get_boolean("Port", str(p)) or not mem.get_boolean("Actuator", str(p)):
                    Tools.setup_actuator(p, content["2"][str(p)])

                mem.set_boolean("Actuator", str(p), True)
                mem.set_boolean("Port", str(p), True)
                mem.set_int("Default", str(p), int(content["2"][str(p)]))
                Tools.set_actuator(p, content["1"][str(p)])

        except Exception as err:
            print(err)
        time.sleep(0.5)

if __name__ == "__main__":
    main()