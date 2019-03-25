import sys
sys.path.append("./../..")
sys.path.append("./..")
sys.path.append("./")

import time
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

    def get_reportdata(self):
        '''
        获取汇报服务器的数据
        Get(or generate) the data which is aim for reporting
        :return: data
        '''
        return '{"data":"%s"}' % str(self.value.value)

    def handle_cmd(self, cmd):
        '''
        处理来自服务器的指令
        Handle the command from server
        :param cmd: 指令 / Command
        '''
        goal = None
        if cmd['data'] == 'on':
            print("Light : On")
            goal = True
        if cmd['data'] == 'off':
            print("Light : Off")
            goal = False

        if (goal is not None) and self.value.value != goal:
            self.value.value = goal
            self.change.value = True
        else:
            self.change.value = False

def main():
    # GPIO
    lightGPIO = [2, 3, 4]
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(lightGPIO, GPIO.OUT)
    GPIO.output(lightGPIO, GPIO.LOW)
    # 新建硬件对象 / Create hardware object
    # 服务器地址, 硬件ID, 硬件类型, 验证口令
    # Server, Hardware Id, Hardware type, Authenicate key
    light = Light(('95.179.154.249', 50001), "raspi", "LightDevice", "QQQ")

    # 开启发送数据线程 / Start the thread for reporting data
    light.report(light.get_reportdata)

    # 开启接收命令线程 / Start the thread for receiving command
    light.receive(light.handle_cmd)

    # 保持运行 & 额外处理 / Keep & Do something else
    while True:
        if not light.online.value:
            GPIO.output(lightGPIO, GPIO.LOW)
            GPIO.output(lightGPIO[0], GPIO.HIGH)
        else:
            if light.value.value:
                GPIO.output(lightGPIO, GPIO.HIGH)
            else:
                GPIO.output(lightGPIO, GPIO.LOW)
        time.sleep(0.5)

if __name__ == '__main__': main()