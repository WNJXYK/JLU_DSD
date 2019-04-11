import sys, json
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

import RPi.GPIO as GPIO
from Demo.Hardware.Hardware import Hardware

class Light(Hardware):

    def __init__(self, addr, hid, typ, auth):
        '''
        声明一些硬件所需要的数据
        Declare some values which is needed
        '''
        super(Light, self).__init__(addr, hid, typ, auth)
        self.value = self.manager.Value('b', False)
        self.msg = self.manager.dict()

    def get_reportdata(self):
        '''
        获取汇报服务器的数据
        Get(or generate) the data which is aim for reporting
        :return: data
        '''
        msg = self.msg.copy()
        self.msg.clear()
        msg["data"] = str(self.value.value)
        return json.dumps(msg)

    def handle_cmd(self, cmd_str):
        '''
        处理来自服务器的指令
        Handle the command from server
        :param cmd_str: 指令 / Command
        '''
        cmd = json.loads(cmd_str)
        print(cmd)

        goal = None
        if cmd['data'] == 'on':
            goal = True
        if cmd['data'] == 'off':
            goal = False

        if (goal is not None) and self.value.value != goal:
            self.value.value = goal
            print("Light : ", goal)
            msg = self.msg.copy()
            msg["cmd"] = cmd_str
            self.msg = msg
            self.commit_report()

def main():
    # GPIO
    lightGPIO = [2, 3, 4]
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(lightGPIO, GPIO.OUT)
    GPIO.output(lightGPIO, GPIO.LOW)
    # 新建硬件对象 / Create hardware object
    # 服务器地址, 硬件ID, 硬件类型, 验证口令
    # Server, Hardware Id, Hardware type, Authenicate key
    light = Light(('39.106.7.29', 1024), "raspi", "Light", "WNJXYK")

    # 开启发送数据线程 / Start the thread for reporting data
    light.report(light.get_reportdata)

    # 开启接收命令线程 / Start the thread for receiving command
    light.receive(light.handle_cmd)

    # 保持运行 & 额外处理 / Keep & Do something else
    try:
        while True:
            if not light.online.value:
                GPIO.output(lightGPIO, GPIO.LOW)
                GPIO.output(lightGPIO[0], GPIO.HIGH)
            else:
                if light.value.value:
                    GPIO.output(lightGPIO, GPIO.HIGH)
                else:
                    GPIO.output(lightGPIO, GPIO.LOW)
    finally:
        GPIO.output(lightGPIO, GPIO.LOW)
        GPIO.cleanup()

if __name__ == '__main__': main()