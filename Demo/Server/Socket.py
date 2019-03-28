import socket, json
from threading import Thread
from Demo.Database import Database


class Socket(object):
    def __init__(self, manager, hardware):
        self.socket_connection = manager.dict()
        self.socket_server = None
        self.hardware = hardware
        self.inQue = manager.Queue(100)
        self.outQue = manager.Queue(100)
        self.auth = "WNJXYK"

    def run(self, address=('0.0.0.0', 3389), auth = "WNJXYK"):
        '''
        启动负责与硬件互联的套接字
        Start the socket which is responsible for communicating with hardware
        :param address: 运行地址 / Listening Address
        '''

        self.auth = auth

        # 新建 Socket / Create a socket
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.bind(address)
        self.socket_server.listen(5)

        # 监听线程 / Listening thread
        thread = Thread(target=self.accept)
        thread.setDaemon(True)
        thread.start()

        # 监听指令队列线程 / Listening command queue thread
        thread = Thread(target=self.send_thread)
        thread.setDaemon(True)
        thread.start()

        print(" * Socket is running on %s:%d\n" % address)

    def send_thread(self):
        '''
        监听命令队列
        Listen the command queue
        '''
        while True:
            (hid, msg) = self.outQue.get(True)
            try:
                self.socket_connection[hid].send(msg.encode("utf8"))
            except: pass

    def accept(self):
        '''
        接受来自硬件的连接
        Accept the hardware
        :return:
        '''
        while True:
            client, _ = self.socket_server.accept()
            thread = Thread(target=self.handle, args=(client,))
            thread.setDaemon(True)
            thread.start()

    def handle(self, client):
        '''
        处理来自硬件的数据
        Solve the data from hardware
        :param client:
        :return:
        '''
        try:
            # 硬件注册消息 / Hardware register message
            hello = json.loads(client.recv(1024))
            hid, typ, auth = hello["id"], hello["type"], hello["auth"]

            # 校验口令 / Authenticate
            if auth != self.auth:
                client.send('{"status":-1, "msg":"Authenticate Failed."}'.encode("utf8"))
                client.close()
                print("%s(%s) authenticate failed" % (typ, hid))
                return

            # 与数据库核对硬件是否注册 / Check this hardware is registered in database
            if not Database.is_hardware(hid):
                client.send('{"status":-3, "msg":"Not An Registered Hardware."}'.encode("utf8"))
                client.close()
                print("%s(%s) is not a registered hardware." % (typ, hid))
                return

            # 处理汇报数据 / Handle the reported data
            if hello["socket"] == "in":
                self.handle_in(client, hid, typ)

            # 注册接受指令硬件 / Register a command-receiving hardware
            if hello["socket"] == "out":
                self.register_out(client, hid, typ)


        except: pass

    def handle_in(self, client, hid, typ):
        '''
        处理传感器与设备汇报的数据
        Handle the data that the hardware reported
        :param client: Socket
        :param hid: 硬件ID / Hardware ID
        :param typ: 硬件类型 / Hardware Type
        '''
        self.hardware.online(hid, typ)  # 硬件上线 / Hareware online
        client.send('{"status":0, "msg":"Hello Device."}'.encode("utf8"))  # 握手信息 / Confirm message

        print("Reporter : %s(%s) is online." % (typ, hid))

        # 循环处理消息 / Solve message in a loop
        while True:
            bytes = client.recv(1024)
            print(bytes)
            if len(bytes) == 0:
                client.close()  # 关闭连接 / Close socket
                self.hardware.offline(hid)  # 硬件下线 / Hardware offline
                print("Reporter : %s(%s) is offline" % (typ, hid))
                return
            else:
                self.hardware.report(hid, bytes)  # 存储硬件数据 / Save hardware data
                if len(bytes) > 2:
                    self.inQue.put(hid)  # 消息进入待处理队列 / Push into queue and wait for handling

    def register_out(self, client, hid, typ):
        '''
        将命令接收硬件进行注册
        Register a command-receiving hareware
        :param client: Socket
        :param hid: 硬件ID / Hardware ID
        :param typ: 硬件类型 / Hardware Type
        :return:
        '''

        # 验证设备是否可以接收命令 / Authenticate whether this hardware is operable
        if not Database.is_device(hid):
            client.send('{"status":-2, "msg":"Not An Registered Device."}'.encode("utf8"))
            client.close()
            print("%s(%s) : Not A Registered Device." % (typ, hid))
            return

        client.send('{"status":0, "msg":"Hello Device."}'.encode("utf8"))  # 握手信息 / Confirm message
        self.socket_connection[hid] = client  # 记录在案 / Record

        print("Receiver : %s(%s) is online." % (typ, hid))


