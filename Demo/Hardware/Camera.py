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

    # 新建硬件对象 / Create hardware object
    # 服务器地址, 硬件ID, 硬件类型, 验证口令
    # Server, Hardware Id, Hardware type, Authenicate key
    camera = Camera(('127.0.0.1', 10000), "popoqqq", "Camera", "WNJXYK")

    # 开启发送数据线程 / Start the thread for reporting data
    camera.report(camera.get_reportdata)

    # 保持运行 & 额外处理 / Keep & Do something else
    while True:
        input()
        camera.value.value = not camera.value.value
        camera.change.value = True
        time.sleep(1)

if __name__ == '__main__': main()