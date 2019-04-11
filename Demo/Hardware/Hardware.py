import socket
from multiprocessing import Manager
from threading import Thread
import json, time


class Hardware(object):

    def __init__(self, addr, hid, typ, auth, heartbeat=2):
        '''
        构造函数 / Construction
        :param addr: 服务器地址 / Server IP:Port
        :param hid: 硬件ID / Hardware ID
        :param typ: 硬件类型 / Hardware Type
        :param auth: 验证口令 / Authenticate Key
        '''
        self.manager = Manager()
        self.change = self.manager.Value('b', False)
        self.online = self.manager.Value('b', False)
        self.reconn = self.manager.Value('b', False)
        self.addr = addr
        self.hid = hid
        self.typ = typ
        self.auth = auth
        self.heartbeat = heartbeat
        self.heartbeat_rate = 0

    def commit_report(self):
        '''
        确定向服务器提交数据
        Commit data to server
        :return:
        '''
        self.change.value = True

    def report_socket(self, func):
        '''
        向服务器汇报数据线程
        Thread for reporting data to server
        :param func: 获取发送数据的函数 / Function for get reported data
        '''
        while True:
            try:
                # 连接并发送注册数据包 / Connect and send register package
                socket_out = socket.socket()
                socket_out.connect(self.addr)
                socket_out.send(('{"id":"%s", "type":"%s", "socket":"in", "auth":"%s"}'%(self.hid, self.typ, self.auth)).encode("utf8"))
                socket_out.settimeout(10)
                # 收取服务器握手信息 / Receive server conform message
                hello = json.loads(socket_out.recv(1024).decode("utf8"))
                if int(hello["status"]) != 0:
                    print("Reporter Error : %s" % hello["msg"])
                    continue
                else: print("Reporter : Connected")

                # 准备汇报初始状态 / Report initial data
                self.change.value = True

                # 循环汇报状态 / Report data in a loop
                while True:
                    self.online.value = True # 设置自身在线判断 / Set online or offline
                    if self.change.value:
                        msg = func()  # 生成汇报数据 / Generate reported data
                        socket_out.send(msg.encode("utf8"))
                        self.change.value = False
                        self.heartbeat_rate = 0

                    if self.heartbeat_rate > self.heartbeat > 0:
                        socket_out.send("{}".encode("utf8"))
                        self.heartbeat_rate = 0

                    self.heartbeat_rate += 0.5
                    time.sleep(0.5)

            except Exception as err:
                print(err)
            finally:
                self.online.value = False
                # 掉线重连 / Reconnect
                socket_out.close()
                print("Reporter Error : Wait 2s & Reconnecting...")
                time.sleep(2)

    def receive_socket(self, func):
        '''
        从服务器接收命令
        Receive command from server
        :param func: 处理命令的函数 / Function for handling command
        '''
        while True:
            try:
                # 连接并发送注册数据包 / Connect and send register package
                socket_in = socket.socket()
                socket_in.connect(self.addr)
                socket_in.send(('{"id":"%s", "type":"%s", "socket":"out", "auth":"%s"}' % (self.hid, self.typ, self.auth)).encode("utf8"))

                # 收取服务器握手信息 / Receive server conform message
                hello = json.loads(socket_in.recv(1024).decode("utf8"))
                if int(hello["status"]) != 0:
                    print("Receiver Error : %s" % hello["msg"])
                    continue
                else: print("Receiver : Connected")

                # 循环接收命令状态 / Receive command in a loop
                while True:
                    try:
                        cmd = socket_in.recv(1024).decode("utf8")
                        if len(cmd) == 0: break  # 掉线判断 / Judge whether offline
                        if self.reconn.value == True:
                            self.reconn.value = False
                            break
                        # cmd = json.loads(cmd)  # 格式化 Json 形式为 Dict / Turn json into dict
                        func(cmd)  # 执行指令
                    except: print("Unknown command : %s" % cmd)

            except Exception as err:
                print(err)
            finally:
                # 掉线重连 / Reconnect
                socket_in.close()
                print("Receiver Error : Wait 2s & Reconnecting...")
                time.sleep(2)

    def receive(self, func):
        '''
        开启接收命令线程
        Start the thread for receiving command
        :param func: 获取发送数据的函数 / Function for get reported data
        '''
        thread = Thread(target=self.receive_socket, args=(func, ))
        thread.setDaemon(True)
        thread.start()

    def report(self, func):
        '''
        开启发送数据线程
        Start the thread for sending data
        :param func: 处理命令的函数 / Function for handling command
        :return:
        '''
        report = Thread(target=self.report_socket, args=(func, ))
        report.setDaemon(True)
        report.start()


