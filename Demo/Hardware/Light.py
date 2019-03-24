import time
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

    # 新建硬件对象 / Create hardware object
    # 服务器地址, 硬件ID, 硬件类型, 验证口令
    # Server, Hardware Id, Hardware type, Authenicate key
    light = Light(('127.0.0.1', 1024), "qwerty", "LightDevice", "Auth")

    # 开启发送数据线程 / Start the thread for reporting data
    light.report(light.get_reportdata)

    # 开启接收命令线程 / Start the thread for receiving command
    light.receive(light.handle_cmd)

    # 保持运行 & 额外处理 / Keep & Do something else
    while True:
        input()
        light.value.value = not light.value.value
        light.change.value = True
        time.sleep(1)

if __name__ == '__main__': main()