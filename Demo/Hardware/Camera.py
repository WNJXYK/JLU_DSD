import sys, getopt
sys.path.append(sys.path[0] + "/../..")
sys.path.append(sys.path[0] + "/..")

import time
from Demo.Hardware.Hardware import Hardware


class Camera(Hardware):

    def __init__(self, addr, hid, typ, auth):
        '''
        声明一些硬件所需要的数据
        Declare some values which is needed
        '''
        super(Camera, self).__init__(addr, hid, typ, auth)
        self.value = self.manager.Value('b', False)

    def get_reportdata(self):
        '''
        获取汇报服务器的数据
        Get(or generate) the data which is aim for reporting
        :return: data
        '''
        return '{"data":"%s"}' % str(self.value.value)

def main():
    # 获取调用参数 / Get Option
    addr = ('127.0.0.1', 1024)
    auth = "WNJXYK"
    hid = "popoqqq"
    typ = "Camera"
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
    camera = Camera(addr, hid, typ, auth)

    # 开启发送数据线程 / Start the thread for reporting data
    camera.report(camera.get_reportdata)

    # 保持运行 & 额外处理 / Keep & Do something else
    while True:
        input()
        print("Sent")
        camera.value.value = not camera.value.value
        camera.commit_report()
        time.sleep(0.1)

if __name__ == '__main__': main()