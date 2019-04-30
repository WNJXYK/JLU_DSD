import sys, getopt
from multiprocessing import Manager
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

import time, json
from Demo.Hardware.Hardware import Hardware

manager = Manager()
m_last = manager.dict()



class Light(Hardware):
    def __init__(self, addr, hid, typ, auth, idx):
        '''
        声明一些硬件所需要的数据
        Declare some values which is needed
        '''
        super(Light, self).__init__(addr, hid, typ, auth)
        self.value = self.manager.Value('b', False)
        self.msg = self.manager.dict()
        self.idx = idx

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

        global m_last
        print(self.idx, "AVE", time.time() - m_last[self.idx])

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




class Button(Hardware):

    def __init__(self, addr, hid, typ, auth):
        '''
        声明一些硬件所需要的数据
        Declare some values which is needed
        '''
        super(Button, self).__init__(addr, hid, typ, auth)
        self.value = self.manager.Value('b', False)

    def get_reportdata(self):
        '''
        获取汇报服务器的数据
        Get(or generate) the data which is aim for reporting
        :return: data
        '''
        return '{"data":"%s"}' % str(self.value.value)

def main():
    MAX_DEVICE = 100
    global m_last

    # 获取调用参数 / Get Option
    addr = ('127.0.0.1', 1024)
    auth = "WNJXYK"
    opts, args = getopt.getopt(sys.argv[1:], "i:p:k:t:h:")
    for op, value in opts:
        if op == "-i": addr = (value, addr[1])
        if op == "-p": addr = (addr[0], int(value))
        if op == "-k": auth = value

    # 批量创建
    create_time = time.time()
    button, light = [], []
    for i in range(MAX_DEVICE):
        light.append(Light(addr, ("%d_Light" % i), "Light", auth, i))
        button.append(Button(addr, ("%d_Button" % i), "ButtonSensor", auth))
    print("Create ", time.time()-create_time)

    connect_time = time.time()
    # 批量链接
    for i in range(MAX_DEVICE):
        light[i].report(light[i].get_reportdata)
        light[i].receive(light[i].handle_cmd)
        button[i].report(button[i].get_reportdata)
    print("Connect", time.time()-connect_time)


    # 保持运行 & 额外处理 / Keep & Do something else
    while True:
        cnt_send_time = sum_send_time = 0
        for i in range(MAX_DEVICE):
            print(i, "Open")
            m_last[i] = time.time()
            button[i].value.value = True
            button[i].commit_report()

        time.sleep(5)
        for i in range(MAX_DEVICE):
            print(i, "Close")
            button[i].value.value = False
            button[i].commit_report()

        time.sleep(5)

if __name__ == '__main__': main()