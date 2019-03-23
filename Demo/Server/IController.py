from Demo.Database import Database

class IController(object):
    def __init__(self, hardware, controller, socket):
        self.hardware = hardware
        self.controller = controller
        self.socket = socket

    # Intelligence Controller
    def IC_generateRoom(self, rid):
        # Generate List
        hardware_list = Database.get_hardwareList(rid)
        device_id = Database.get_roomDevice(rid)
        sensors = []
        for hid in hardware_list:
            if device_id == hid : continue
            sensors.append(self.hardware.get(hid))
        return sensors, device_id

    def IC_report(self, id):
        # Get Affected Room
        rooms = Database.get_roomList(id, False)
        for room in rooms:
            sensors, device = self.IC_generateRoom(room)
            if id == device: continue
            msg = self.controller.Run({"sensors":sensors, "device": self.hardware.get(device), "cmd" : "", "authority": 0})
            print(device, msg)
            try:
                self.socket[device].send(msg.encode("utf8"))
            except: pass

    def IC_command(self, hid, uid, cmd):
        info = Database.get_hardwareInfo(hid)
        if info["type"] != 1 : return '{"status":-2, "msg":"You can not operate a sensor."}'
        # Get Affected Room
        rooms = Database.get_roomList(hid, False)
        # Get User
        user = Database.get_user(uid)
        for room in rooms:
            print(hid, room)
            sensors, device = self.IC_generateRoom(room)
            msg = self.controller.Cmd({"sensors":sensors, "device": self.hardware.get(device), "cmd" : cmd, "authority": user["authority"]})
            print(device, msg)
            try:
                self.socket[device].send(msg.encode("utf8"))
            except:
                return '{"status":-1, "msg":"Device busy or offline."}'

        return '{"status":0, "msg":"Message sent."}'
