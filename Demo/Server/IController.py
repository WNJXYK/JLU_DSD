from threading import Thread
from Demo.Database import Database
import time


class IController(object):
    '''
    与智能控制模块的接口
    Interface between controller and server
    '''

    def __init__(self, hardware, controller, socket):
        self.hardware = hardware
        self.controller = controller
        self.socket = socket

        # 监听硬件消息线程 / A thread that listening message from hardware
        thread = Thread(target=self.report_thread)
        thread.setDaemon(True)
        thread.start()

    def report_thread(self):
        '''
        持续读取硬件消息队列线程
        Thread for reading queue of hardware' message
        '''
        while True:
            hid = self.socket.inQue.get(True)
            self.report(hid)

    def room_info(self, rid):
        '''
        获取房间内传感器数据与设备编号 / Get sensors' data and device ID in the room
        :param rid: 房间编号 / Room ID
        :returns: 传感器数据列表, 设备编号 / Sensors's data list, Device ID
        '''
        hardware_list = Database.get_hardwareList(rid)
        device_id = Database.get_roomDevice(rid)
        sensors = []
        for hid in hardware_list:
            if device_id == hid : continue
            sensors.append(self.hardware.get(hid))
        return sensors, device_id

    def report(self, hid):
        '''
        传感器、设备更新时，更新受影响的房间的设备状态 / When sensors' and device's data changed, update the state of device in affected rooms
        :param hid: 硬件ID / Hardware ID
        '''

        # 当设备自更新时，不向控制器反馈 / When a device updated its self, don't report to controller
        info = Database.get_hardwareInfo(hid)
        if info["type"] == 1:
            return

        # 获取受影响房间编号列表 / Get the list of affected rooms' ID
        rooms = Database.get_roomList(hid, False)

        for rid in rooms:
            # 生成控制数据 / Generate data which controller needed
            sensors, device = self.room_info(rid)
            param = {
                "sensors": sensors,
                "device": self.hardware.get(device),
            }

            # 控制 / Control
            msg = self.controller.Run(param)

            # 向设备发送控制信号 / Send a signal to hardware
            self.socket.outQue.put((device, msg))

    def command(self, hid, uid, cmd):
        '''
        用户发出指令时，更新受影响的房间的设备状态 / When user has sent a command, update the state of device in affected rooms

        状态 / Status :
        -1 : 不允许操作的硬件 / This hardware cannot be operated
        -2 : 设备离线 / Device offline
        0 : 操作成功 / operate successfully

        :param hid: 硬件ID / Hardware ID
        :param uid: 用户ID / User ID
        :param cmd: 命令 / Command
        :return: 操作状态 / result
        '''

        # 不允许用户操作传感器 / User cannot operator a sensor
        info = Database.get_hardwareInfo(hid)
        if info["type"] != 1 :
            return { "status": -1, "msg": "You can not operate a sensor."}
        if self.hardware.get(hid)["online"] == 0:
            return {"status": -2, "msg": "Device is offline."}

        # 获取受影响房间编号列表 / Get the list of affected rooms' ID
        rooms = Database.get_roomList(hid, False)

        # 获取用户信息 / Get User Info
        user = Database.get_user(uid)

        for rid in rooms:
            # 生成控制数据 / Generate data which controller needed
            sensors, device = self.room_info(rid)
            param = {
                "sensors": sensors,
                "device": self.hardware.get(device),
                "cmd": cmd,
                "authority": user["authority"]
            }

            # 控制 / Control
            msg = self.controller.Cmd(param)

            # 向设备发送控制信号 / Send a signal to hardware
            self.socket.outQue.put((device, msg))

        return {"status": 0, "msg": "Message sent."}

    def heartbeat_thread(self, duration):
        '''
        向控制模块定时激活所有房间
        Active controller periodically for every room
        :param duration: 延时 / delay
        '''
        while True:
            try:
                # 定时激活所有房间
                rooms = Database.get_allRoom()

                for rid in rooms:
                    # 生成控制数据 / Generate data which controller needed
                    sensors, device = self.room_info(rid)
                    param = {
                        "sensors": sensors,
                        "device": self.hardware.get(device),
                    }

                    # 控制 / Control
                    msg = self.controller.Run(param)

                    # 向设备发送控制信号 / Send a signal to hardware
                    self.socket.outQue.put((device, msg))

                # 定时睡眠
                time.sleep(duration)
            except: pass

    def heartbeat(self, duration):
        thread = Thread(target = self.heartbeat_thread, args = (duration, ))
        thread.setDaemon(True)
        thread.start()