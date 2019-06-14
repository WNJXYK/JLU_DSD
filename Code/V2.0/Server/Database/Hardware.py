from Server.Database import IDatabase
from Server import Config
import json
import uuid, time

def add_raspi(name = None):
    # Generate Unique ID
    uid_flag = True
    while uid_flag:
        uid = str(uuid.uuid4())
        _, cnt = IDatabase.render("SELECT COUNT(*) FROM Raspi WHERE uid = ?", (uid, ))
        if cnt[0][0] == 0: uid_flag = False

    # Insert Raspi
    content = json.dumps({"0": {}, "1": {}, "2": {}})
    sql = "INSERT INTO Raspi (uid, content, online, last, name) VALUES ('%s', '%s', 1, %f, '%s')" % (uid, content, time.time(), name if name is not None else "Legacy Version")
    IDatabase.render(sql)

    return 0, "", uid


def check_raspi(id):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Raspi WHERE id = ?", (id, ))
    return 0 if cnt[0][0]>0 else 1, ""


def del_raspi(id):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Raspi WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such Raspi"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Hardware WHERE host = ?", (id,))
    if cnt[0][0] > 0: return 2, "There are still Hardware attached on this raspi"

    IDatabase.render("DELETE FROM Hardware where host = ?", (id, ))
    IDatabase.render("DELETE FROM Raspi where id = ?", (id,))
    return 0, ""

def list_raspi():
    _, raspi = IDatabase.render("SELECT id, uid, online, name FROM Raspi")

    ret = []
    for r in raspi:
        update_raspi(r[0])

        _, cnt = IDatabase.render("SELECT COUNT(*) FROM Hardware WHERE host = ?", (r[0],))

        ret.append({"id": r[0], "uid": r[1], "online": r[2], "hardware": cnt[0][0], "name": r[3]})

    return 0, "", ret

def query_raspi_id(uid):
    _, id = IDatabase.render("SELECT id FROM Raspi WHERE uid = ?", (uid, ))
    if len(id) == 0: return -1
    return id[0][0]

def update_raspi(id, data = {"0": {}, "1": {}, "2": {}}, last = None):
    _, hList = IDatabase.render("SELECT id, type, gpio, value, defaultValue FROM Hardware WHERE host = ?", (id, ))
    content = {"0": {}, "1": {}, "2": {}}
    # 0: Sensor 1: Actuator 2: Default for Actuator

    # Sync data between Virtual Hardware & Real Raspi
    for hardware in hList: update_hardware(hardware[0])
    for hardware in hList:
        hardware_id, type, gpio, value, defaultValue = hardware[0], hardware[1], hardware[2], hardware[3], hardware[4]
        _, func = IDatabase.render("SELECT func FROM HardwareType WHERE id = ?", (type, ))
        func = func[0][0]
        content[str(func)][str(gpio)] = value
        if func == 1: content["2"][str(gpio)] = defaultValue
        if func == 0 and str(gpio) in data["0"]:
            content["0"][str(gpio)] = data["0"][str(gpio)]

    # Update Content
    IDatabase.render("UPDATE Raspi SET content = ? WHERE id = ?", (json.dumps(content), id, ))

    # Update Online State
    _, raspi_last = IDatabase.render("SELECT last, content FROM Raspi WHERE id = ?", (id, ))
    raspi_last = raspi_last[0][0]
    if last is not None: raspi_last = last
    online = 1
    if time.time()-raspi_last > Config.ONLINE_THRESHOLD: online = 0
    IDatabase.render("UPDATE Raspi SET online = ?, last = ? WHERE id = ?", (online, raspi_last, id, ))

    # Update Hardware
    for hardware in hList: update_hardware(hardware[0])

    return content


def add_hardware(name, type, host, gpio, room):
    _, content = IDatabase.render("SELECT content FROM Raspi WHERE id = ?", (host, ))
    if len(content) == 0: return 1, "No Such Raspberry Pi"

    content = json.loads(content[0][0])

    # Check GPIO
    if gpio == "Camera" and int(type)==4:
        pass
    elif gpio == "I2C" and int(type)==3:
        pass
    else:
        if int(type)==4: return 3, "Camera Must Use 'Camera' as GPIO ID"
        if int(type)==3: return 4, "Light Sensor Must Use 'I2C' as GPIO ID"
        if gpio in ["Camera" or "I2C"]: return 5, "Only Special Sensor Can Use Special GPIO ID"
        raspi_range = [7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
        if int(gpio) not in raspi_range: return 6, "GPIO should in range [1, 40] without Power & Ground & I2C"
    if str(gpio) in content["0"]: return 2, "GPIO Has Been Using"
    if str(gpio) in content["1"]: return 2, "GPIO Has Been Using"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Room WHERE id = ?", (room,))
    if cnt[0][0] == 0: return 3, "No Such Room"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM HardwareType WHERE id = ?", (type,))
    if cnt[0][0] == 0: return 4, "No Such Hardware Type"

    _, defaultValue = IDatabase.render("SELECT defaultValue FROM Room WHERE id = ?", (room,))
    defaultValue = defaultValue[0][0]

    IDatabase.render("INSERT INTO Hardware (name, type, host, gpio, room, value, defaultValue, online) VALUES ('%s', %d, %d, '%s', %d, 0, %d, 1)" % (name, type, host, str(gpio), room, int(defaultValue)))
    update_raspi(host)

    return 0, ""


def modify_hardware(id, name, room, defaultValue):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Hardware WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such Hardware"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Room WHERE id = ?", (room,))
    if cnt[0][0] == 0: return 2, "No Such Room"

    try:
        if int(defaultValue) != 0 and int(defaultValue) != 1: return 3, "Invalid Default Value"
    except:
        return 3, "Invalid Default Value"

    IDatabase.render("UPDATE Hardware SET name = ?, room = ?, defaultValue = ? WHERE id = ?", (name, room, defaultValue, id, ))


def del_hardware(id):
    _, host = IDatabase.render("SELECT host FROM Hardware WHERE id = ?", (id, ))
    if len(host) == 0: return 1, "No Such Hardware"
    host = host[0][0]

    IDatabase.render("DELETE FROM Hardware where id = ?", (id,))
    update_raspi(host)

    return 0, ""

def update_hardware(id):
    _, hardware = IDatabase.render("SELECT host, type, gpio FROM Hardware WHERE id = ?", (id,))
    if len(hardware) == 0: return 1, "No Such Hardware", None
    host, gpio = hardware[0][0], hardware[0][2]
    _, type = IDatabase.render("SELECT func FROM HardwareType WHERE id = ?", (hardware[0][1], ))
    func = type[0][0]

    if func == 0:
        _, content = IDatabase.render("SELECT content, last FROM Raspi WHERE id = ?", (host, ))
        content, last, online = content[0][0], content[0][1], 1
        content = json.loads(content)
        if str(gpio) in content[str(func)]:
            value = content[str(func)][str(gpio)]
            if time.time()-last > Config.ONLINE_THRESHOLD: online = 0
            IDatabase.render("UPDATE Hardware SET value = ?, online = ? WHERE id = ?", (value, online, id, ))
    else:
        _, content = IDatabase.render("SELECT last FROM Raspi WHERE id = ?", (host, ))
        last, online = content[0][0], 1
        if time.time()-last > Config.ONLINE_THRESHOLD: online = 0
        IDatabase.render("UPDATE Hardware SET online = ? WHERE id = ?", (online, id, ))


    return 0, ""


def query_hardware(id):
    _, hardware = IDatabase.render("SELECT name, type, host, gpio, value, id, room, online, defaultValue FROM Hardware WHERE id = ?", (id,))
    if len(hardware) == 0: return 1, "No Such Hardware", None

    update_hardware(id)

    hardware = hardware[0]
    _, type = IDatabase.render("SELECT name, func FROM HardwareType WHERE id = ?", (hardware[1], ))
    type = type[0]

    ret = {
        "id": hardware[5],
        "room": hardware[6],
        "name": hardware[0],
        "type": type[0],
        "type_id": hardware[1],
        "func": type[1],
        "host": hardware[2],
        "gpio": hardware[3],
        "value": hardware[4],
        "online": hardware[7],
        "default": hardware[8]
    }

    return 0, "", ret


def set_light(id, state):
    if state not in [0, 1]: return 1, "Invalid State"
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Hardware WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 2, "No Such Hardware"

    IDatabase.render("UPDATE Hardware SET value = ? WHERE id = ?", (state, id))
    return 0, ""


def query_hardware_count():
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Hardware")
    return 0, "", cnt[0][0]


def query_raspi_count():
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Raspi")
    return 0, "", cnt[0][0]