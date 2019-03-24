import socket
from multiprocessing import Manager
from threading import Thread
import json, time


class Hardware(object):
    def __init__(self, addr, hid, typ, auth):
        self.manager = Manager()
        self.value = self.manager.Value('b', False)
        self.change = self.manager.Value('b', False)
        self.addr = addr
        self.hid = hid
        self.typ = typ
        self.auth = auth

    # Report State
    def report_socket(self, address, hid, typ, auth, func):
        while True:
            try:
                # 连接并发送注册数据包 / Connect and send register package
                socket_out = socket.socket()
                socket_out.connect(address)
                socket_out.send(('{"id":"%s", "type":"%s", "socket":"in", "auth":"%s"}'%(hid, typ, auth)).encode("utf8"))

                # 收取服务器握手信息 / Receive server conform message
                hello = json.loads(socket_out.recv(1024))
                if int(hello["status"]) != 0:
                    print("Reporter Error : %s" % hello["msg"])
                    continue
                else: print("Reporter : Connected")

                # 准备汇报初始状态 / Report initial data
                self.change.value = True

                # 循环汇报状态 / Report data in a loop
                while True:
                    if self.change.value:
                        msg = func()  # 生成汇报数据 / Generate reported data
                        socket_out.send(msg.encode("utf8"))
                        self.change.value = False
                    time.sleep(0.5)

            except: pass
            finally:
                # 掉线重连 / Reconnect
                socket_out.close()
                print("Reporter Error : Wait 2s & Reconnecting...")
                time.sleep(2)

    # Receive Command
    def receive_socket(self, address, hid, typ, auth, func):
        global light_state, light_change
        while True:
            try:
                # 连接并发送注册数据包 / Connect and send register package
                socket_in = socket.socket()
                socket_in.connect(address)
                socket_in.send(('{"id":"%s", "type":"%s", "socket":"out", "auth":"%s"}' % (hid, typ, auth)).encode("utf8"))

                # 收取服务器握手信息 / Receive server conform message
                hello = json.loads(socket_in.recv(1024))
                if int(hello["status"]) != 0:
                    print("Receiver Error : %s" % hello["msg"])
                    continue
                else: print("Receiver : Connected")

                # 循环接收命令状态 / Receive command in a loop
                while True:
                    try:
                        cmd = socket_in.recv(1024)
                        if len(cmd) == 0: break  # 掉线判断 / Judge whether offline
                        cmd = json.loads(cmd)  # 格式化 Json 形式为 Dict / Turn json into dict
                        func(cmd)  # 执行指令
                    except: print("Unknown command : %s" % cmd)

            except: pass
            finally:
                # 掉线重连 / Reconnect
                socket_in.close()
                print("Receiver Error : Wait 2s & Reconnecting...")
                time.sleep(2)

    def receive(self, func):
        thread = Thread(target=self.receive_socket, args=(self.addr, self.hid, self.typ, self.auth, func))
        thread.setDaemon(True)
        thread.start()

    def report(self, func):
        report = Thread(target=self.report_socket, args=(self.addr, self.hid, self.typ, self.auth, func))
        report.setDaemon(True)
        report.start()


