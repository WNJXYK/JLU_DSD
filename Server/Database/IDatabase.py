import os, json
import sqlite3
import hashlib

PATH = "./database.db"

def md5(s):
    ret = hashlib.md5()
    ret.update(s.encode("utf8"))
    return ret.hexdigest()


def render(sql, param=None):
    global PATH
    conn = sqlite3.connect(PATH)
    c = conn.cursor()

    # print(sql, param)
    # Execute SQL
    if param is None:
        cursor = c.execute(sql)
    else:
        cursor = c.execute(sql, param)

    # Get Result
    ret_cnt, ret = conn.total_changes, []
    while cursor is not None:
        res = cursor.fetchone()
        if res is None: break
        ret.append(res)

    conn.commit()
    conn.close()

    return ret_cnt, ret


def install():
    global PATH
    if os.path.isfile(PATH): return

    ## Create Tables ##
    print(" * Database : Create database")

    # Role Table
    sql_table = '''CREATE TABLE Role
               (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               name TEXT NOT NULL,
               priority INTEGER NOT NULL,
               permission TEXT NOT NULL);'''
    render(sql_table)

    # Raspi Table
    sql_table = '''CREATE TABLE Raspi
               (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               uid TEXT NOT NULL,
               content TEXT NOT NULL,
               online INTEGER NOT NULL,
               last DECIMAL NOT NULL);'''
    render(sql_table)

    # Hardware Table
    sql_table = '''CREATE TABLE Hardware
               (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               name TEXT NOT NULL,
               type INTEGER NOT NULL,
               host INTEGER NOT NULL,
               gpio INTEGER NOT NULL,
               room INTEGER NOT NULL,
               value INTEGER NOT NULL,
               online INTEGER NOT NULL,
               defaultValue INTEGER NOT NULL,
               FOREIGN KEY (room) REFERENCES Room(id),
               FOREIGN KEY (host) REFERENCES Raspi(id),
               FOREIGN KEY (type) REFERENCES HardwareType(id));'''
    render(sql_table)

    # Hardware Type Table
    sql_table = '''CREATE TABLE HardwareType
               (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               name TEXT NOT NULL,
               func INTEGER NOT NULL);'''
    render(sql_table)

    # User
    sql_table = '''CREATE TABLE User
               (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               user TEXT NOT NULL,
               name TEXT NOT NULL,
               password TEXT NOT NULL,
               token TEXT NOT NULL,
               role INTEGER NOT NULL,
               permission TEXT NOT NULL,
               FOREIGN KEY (role) REFERENCES Role(id));'''
    render(sql_table)

    # Room
    sql_table = '''CREATE TABLE Room
               (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               name TEXT NOT NULL,
               building INTEGER NOT NULL,
               status INTEGER NOT NULL,
               timeout DECIMAL NOT NULL,
               defaultValue INTEGER NOT NULL,
               FOREIGN KEY (building) REFERENCES Building(id));'''
    render(sql_table)

    # Building
    sql_table = '''CREATE TABLE Building
               (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               name TEXT NOT NULL,
               status INTEGER NOT NULL);'''
    render(sql_table)

    # Building
    sql_table = '''CREATE TABLE Log
                   (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   room INTEGER NOT NULL,
                   building INTEGER NOT NULL,
                   solved INTEGER NOT NULL);'''
    render(sql_table)

    # Insert Hardware Type
    render("INSERT INTO HardwareType (id, name, func) VALUES (1, 'Light', 1)")
    render("INSERT INTO HardwareType (id, name, func) VALUES (2, 'Alarm', 1)")
    render("INSERT INTO HardwareType (id, name, func) VALUES (3, 'Light Sensor', 0)")
    render("INSERT INTO HardwareType (id, name, func) VALUES (4, 'Presence Sensor', 0)")
    render("INSERT INTO HardwareType (id, name, func) VALUES (5, 'Button', 0)")
    render("INSERT INTO HardwareType (id, name, func) VALUES (6, 'Panic Button', 0)")

    # Insert Policy
    render("INSERT INTO Role (id, name, priority, permission) VALUES (3, 'Student', 1, '%s')" % json.dumps({"admin": 0, "build":0, "force":0}))
    render("INSERT INTO Role (id, name, priority, permission) VALUES (2, 'Teacher', 2, '%s')" % json.dumps({"admin": 0, "build":1, "force": 1}))
    render("INSERT INTO Role (id, name, priority, permission) VALUES (1, 'Administrator', 3, '%s')" % json.dumps({"admin": 1, "build":1, "force": 0}))

    # Insert Admin
    render("INSERT INTO User (user, name, password, role, token, permission) VALUES ('admin', '管理员', '%s', 1, '', '{}')" % md5("admin" + "#" + "admin"))
    render("INSERT INTO User (user, name, password, role, token, permission) VALUES ('teacher', '教师', '%s', 2, '', '{}')" % md5("teacher" + "#" + "teacher"))
    render("INSERT INTO User (user, name, password, role, token, permission) VALUES ('wnjxyk', '喂你脚下有坑', '%s', 3, '', '{}')" % md5("wnjxyk" + "#" + "wnjxyk"))
    print(" * Database : Admin Password " + md5("admin" + "#" + "admin"))

if __name__ == '__main__':
    install()
