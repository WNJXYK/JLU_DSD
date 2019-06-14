from Server.Database import IDatabase
from Server.Database import Room
from Server import Config
import json
import uuid, time

def add_log(building, room):
    _, status = IDatabase.render("SELECT status FROM Building WHERE id = ?", (building, ))
    if status[0][0]==1: return 0, ""

    IDatabase.render("INSERT INTO Log (room, building, solved) VALUES (%d, %d, 0)" % (int(room), int(building)))
    Room.modify_building_status(building, 1)
    return 0, ""


def del_log(id):
    IDatabase.render("UPDATE Log SET solved = 1 WHERE id = ?" , (id, ))
    _, building = IDatabase.render("SELECT building FROM Log WHERE id = ?", (id, ))
    building = building[0][0]
    Room.modify_building_status(building, 0)
    return 0, ""


def list_log():
    _, logs = IDatabase.render("SELECT id, building, room FROM Log WHERE solved = 0")
    ret = []
    for log in logs:
        ret.append({"id": log[0], "building": log[1], "room": log[2]})
    return 0, "", ret