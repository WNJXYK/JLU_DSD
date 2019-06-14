from Server.Database import IDatabase
from Server.Database import Hardware


def add_room(name, building, timeout, defaultValue):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Building WHERE id = ?", (building,))
    if cnt[0][0] == 0: return 1, "No Such Building"

    try:
        if int(defaultValue) not in [0, 1]: return 1, "Invalid Default Value"
    except:
        return 1, "Invalid Default Value"

    try:
        timeout = float(timeout)
    except:
        return 2, "Invalid Timeout"

    IDatabase.render("INSERT INTO Room (name, building, status, timeout, defaultValue) VALUES ('%s', %d, 0, %f, %d)" % (name, building, timeout, int(defaultValue)))
    return 0, ""


def modify_room(id, name, timeout, defaultValue):
    try:
        if int(defaultValue) not in [0, 1]: return 1, "Invalid Default Value"
    except:
        return 1, "Invalid Default Value"

    try:
        timeout = float(timeout)
    except:
        return 2, "Invalid Timeout"

    _, room = IDatabase.render("UPDATE Room SET name = ?, timeout = ?, defaultValue = ? WHERE id = ?", (name, timeout, defaultValue, id, ))
    _, _, hardware = list_hardware(id)

    for h in hardware:
        Hardware.modify_hardware(h["id"], h["name"], h["room"], defaultValue)

    return 0, ""

def del_room(id):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Room WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such Room"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Hardware WHERE room = ?", (id,))
    if cnt[0][0] > 0: return 2, "there still are hardware in the room."

    IDatabase.render("DELETE FROM Room WHERE id = ?", (id, ))
    return 0, ""


def add_building(name):
    IDatabase.render("INSERT INTO Building (name, status) VALUES ('%s', 0)" % (name, ))
    return 0, ""


def del_building(id):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Building WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such Building"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Room WHERE building = ?", (id,))
    if cnt[0][0] > 0: return 1, "There are rooms in this building."

    IDatabase.render("DELETE FROM Building WHERE id = ?", (id, ))
    return 0, ""


def list_building():
    _, building = IDatabase.render("SELECT id, name, status FROM Building")

    ret = []
    for b in building:
        ret.append({"id": b[0], "name": b[1], "status": b[2]})

    return 0, "", ret


def query_room(id):
    _, room = IDatabase.render("SELECT id, name, status, timeout, defaultValue, building FROM Room WHERE id = ?",(id,))
    r = room[0]

    ret = {"id": r[0], "name": r[1], "status": r[2], "timeout": r[3], "defaultValue": r[4], "building": r[5]}

    return 0, "", ret

def list_room(building):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Building WHERE id = ?", (building,))
    if cnt[0][0] == 0: return 1, "No Such Building", []

    _, room = IDatabase.render("SELECT id, name, status, timeout, defaultValue FROM Room WHERE building = ?", (building, ))

    ret = []
    for r in room:
        ret.append({"id": r[0], "name": r[1], "status": r[2], "timeout": r[3], "defaultValue": r[4]})

    return 0, "", ret


def list_hardware(room):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Room WHERE id = ?", (room,))
    if cnt[0][0] == 0: return 1, "No Such Room", []

    _, hardware = IDatabase.render("SELECT id FROM Hardware WHERE room = ?", (room, ))

    ret = []
    for h in hardware:
        _, _, obj = Hardware.query_hardware(h[0])
        ret.append(obj)
    return 0, "", ret


def modify_room_status(id, status):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Room WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such Room"

    IDatabase.render("UPDATE Room SET status = ? WHERE id = ?", (status, id,))

    return 0, ""


def modify_building_status(id, status):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Building WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such Building"

    IDatabase.render("UPDATE Building SET status = ? WHERE id = ?", (status, id, ))

    _, room = IDatabase.render("SELECT id, name, status FROM Room WHERE building = ?", (id, ))
    for r in room: modify_room_status(r[0], status)

    return 0, ""

def query_building_count():
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Building")
    return 0, "", cnt[0][0]


def query_room_count():
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Room")
    return 0, "", cnt[0][0]