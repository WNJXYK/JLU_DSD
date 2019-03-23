import jsonify
from Demo.Database import Database


class IController(object):
    def __init__(self, hardware, controller, socket):
        self.hardware = hardware
        self.controller = controller
        self.socket = socket

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

        info = Database.get_hardwareInfo(hid)  # 当设备自更新时，不向控制器反馈 / When a device updated its self, don't report to controller
        if info["type"] != 1:
            return

        rooms = Database.get_roomList(hid, False)  # 获取受影响房间编号列表 / Get the list of affected rooms' ID

        for rid in rooms:
            sensors, device = self.room_info(rid)  # 生成控制数据 / Generate data which controller needed
            param = {
                "sensors": sensors,
                "device": self.hardware.get(device),
            }

            msg = self.controller.Run(param)  # 控制 / Control

            try:  # 向设备发送控制信号 / Send a signal to hardware
                self.socket[device].send(msg.encode("utf8"))
            except Exception as err:
                print("IController Error : %s" % err)

    def command(self, hid, uid, cmd):
        '''
        用户发出指令时，更新受影响的房间的设备状态 / When user has sent a command, update the state of device in affected rooms

        状态 / Status :
        -1 : 硬件忙碌或离线 / Device busy or offline
        -2 : 不允许操作的硬件 / This hardware cannot be operated
        0 : 操作成功 / operate successfully

        :param hid: 硬件ID / Hardware ID
        :param uid: 用户ID / User ID
        :param cmd: 命令 / Command
        :return: 操作状态 / result
        '''
        info = Database.get_hardwareInfo(hid) # 不允许用户操作传感器 / User cannot operator a sensor
        if info["type"] != 1 :
            ret = {
                "status": -2,
                "msg": "You can not operate a sensor."
            }
            return ret

        rooms = Database.get_roomList(hid, False)  # 获取受影响房间编号列表 / Get the list of affected rooms' ID

        user = Database.get_user(uid) # 获取用户信息 / Get User Info

        for rid in rooms:
            sensors, device = self.room_info(rid)  # 生成控制数据 / Generate data which controller needed
            param = {
                "sensors": sensors,
                "device": self.hardware.get(device),
                "cmd": cmd,
                "authority": user["authority"]
            }

            msg = self.controller.Cmd(param)  # 控制 / Control

            try:  # 向设备发送控制信号 / Send a signal to hardware
                self.socket[device].send(msg.encode("utf8"))
            except:
                return { "status": -1, "msg": "Device busy or offline." }  

        return { "status":0, "msg":"Message sent." }
