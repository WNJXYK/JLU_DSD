import sys, getopt
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

import time, json
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
        if int(cmd['data']) == 1:
            goal = True
        if int(cmd['data']) == 0:
            goal = False

        if (goal is not None) and self.value.value != goal:
            self.value.value = goal
            print("Light : ", goal)
            msg = self.msg.copy()
            msg["cmd"] = cmd_str
            self.msg = msg
            self.commit_report()

def main():
    # 获取调用参数 / Get Option
    addr = ('127.0.0.1', 1024)
    auth = "WNJXYK"
    hid = "qwerty"
    typ = "Light"
    opts, args = getopt.getopt(sys.argv[1:], "i:p:k:t:h:")
    for op, value in opts:
        if op == "-i": addr = (value, addr[1])
        if op == "-p": addr = (addr[0], int(value))
        if op == "-k": auth = value
        if op == "-t": typ = value
        if op == "-h": hid = value

    # 新建硬件对象 / Create hardware object
    # 服务器地址, 硬件ID, 硬件类型, 验证口令
    # Server, Hardware Id, Hardware type, Authenicate key
    light = Light(addr, hid, typ, auth)

    # 开启发送数据线程 / Start the thread for reporting data
    light.report(light.get_reportdata)

    # 开启接收命令线程 / Start the thread for receiving command
    light.receive(light.handle_cmd)

    # 保持运行 & 额外处理 / Keep & Do something else
    while True:
        input()
        light.value.value = not light.value.value
        light.commit_report()
        time.sleep(0.1)

if __name__ == '__main__': main()