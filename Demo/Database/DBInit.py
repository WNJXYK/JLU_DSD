import hashlib, sqlite3, time

# Settings
PATH = "./database.db"

def md5(s):
    ret = hashlib.md5()
    ret.update(s.encode("utf8"))
    return ret.hexdigest()


def create_user_table():
    global conn, PATH
    conn = sqlite3.connect(PATH)

    # Create User Table
    c = conn.cursor()
    c.execute('''CREATE TABLE User
           (UID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           Nickname TEXT NOT NULL,
           Password TEXT NOT NULL,
           Email TEXT NOT NULL,
           SID TEXT,
           Authority INT NOT NULL);
           ''')

    # Add Init Info
    c.execute("INSERT INTO User (Nickname, Password, Email, SID, Authority) \
            VALUES ('管理员', '%s', 'admin@gmail.com', '%s', 4)" % (md5("admin"), md5(str(time.time()))))
    c.execute("INSERT INTO User (Nickname, Password, Email, SID, Authority) \
                VALUES ('喂你脚下有坑', '%s', 'wnjxyk@gmail.com', '%s', 2)" % (md5("wnjxyk"), md5(str(time.time()))))
    c.execute("INSERT INTO User (Nickname, Password, Email, SID, Authority) \
                    VALUES ('老师', '%s', 'teacher@gmail.com', '%s', 3)" % (md5("teacher"), md5(str(time.time()))))
    conn.commit()

    conn.close()


def create_room_table():
    global conn, PATH
    conn = sqlite3.connect(PATH)

    # Create Room Table
    c = conn.cursor()
    c.execute('''CREATE TABLE Room
           (RID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           Nickname TEXT NOT NULL,
           BID INTEGER,
           SensorCNT INTEGER,
           DeviceCNT INTEGER,
           Details TEXT,
           FOREIGN KEY (BID) REFERENCES Building(BID));
           ''')

    # Add Init Info
    c.execute("INSERT INTO Room (Nickname, Details, BID) VALUES ('Zero', '树莓派测试房间', 1)")
    c.execute("INSERT INTO Room (Nickname, Details, BID) VALUES ('Computer', '电脑控制房间', 2)")
    conn.commit()

    conn.close()

def create_building_table():
    global conn, PATH
    conn = sqlite3.connect(PATH)

    # Create Room Table
    c = conn.cursor()
    c.execute('''CREATE TABLE Building
           (BID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           Nickname TEXT NOT NULL,
           Details TEXT);
           ''')

    # Add Init Info
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Zero', '树莓派测试大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Dormitory', '电脑控制大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Zero', '树莓派测试大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Dormitory', '电脑控制大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Zero', '树莓派测试大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Dormitory', '电脑控制大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Zero', '树莓派测试大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Dormitory', '电脑控制大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Zero', '树莓派测试大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Dormitory', '电脑控制大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Zero', '树莓派测试大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Dormitory', '电脑控制大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Zero', '树莓派测试大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Dormitory', '电脑控制大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Zero', '树莓派测试大楼')")
    c.execute("INSERT INTO Building (Nickname, Details) VALUES ('Building Dormitory', '电脑控制大楼')")
    conn.commit()

    conn.close()


def create_hardware_table():
    global conn, PATH
    conn = sqlite3.connect(PATH)

    # Create Hardware Table
    c = conn.cursor()
    c.execute('''CREATE TABLE Hardware
               (HID TEXT PRIMARY KEY NOT NULL,
               Nickname TEXT NOT NULL,
               Type TEXT,
               Ctrl INTEGER NOT NULL);
               ''')

    # Add Init Info
    c.execute("INSERT INTO Hardware (HID, Nickname, Type, Ctrl) VALUES ('raspi', '测试小灯', 'Light', 1)")
    c.execute("INSERT INTO Hardware (HID, Nickname, Type, Ctrl) VALUES ('qwerty', '寝室灯', 'Light', 1)")
    c.execute("INSERT INTO Hardware (HID, Nickname, Type, Ctrl) VALUES ('popoqqq', '寝室摄像头', 'PresenceSensor', 0)")
    conn.commit()

    conn.close()

def create_rUser_table():
    global conn, PATH
    conn = sqlite3.connect(PATH)

    # Create Hardware Table
    c = conn.cursor()
    c.execute('''CREATE TABLE rUser
               (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               RID INTEGER NOT NULL,
               UID INTEGER NOT NULL,
               FOREIGN KEY (UID) REFERENCES User(UID),
               FOREIGN KEY (RID) REFERENCES Room(RID));
               ''')
    c.execute("INSERT INTO rUser (RID, UID) VALUES (1, 2)")
    conn.commit()

    conn.close()

def create_rHardware_table():
    global conn, PATH
    conn = sqlite3.connect(PATH)

    # Create Hardware Table
    c = conn.cursor()
    c.execute('''CREATE TABLE rHardware
               (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               RID INTEGER NOT NULL,
               HID TEXT NOT NULL,
               FOREIGN KEY (RID) REFERENCES Room(RID),
               FOREIGN KEY (HID) REFERENCES Hardware(HID));
               ''')
    # Add Init Info
    c.execute("INSERT INTO rHardware (HID, RID) VALUES ('raspi', 1)")
    c.execute("INSERT INTO rHardware (HID, RID) VALUES ('popoqqq', 2)")
    c.execute("INSERT INTO rHardware (HID, RID) VALUES ('qwerty', 2)")
    conn.commit()

    conn.close()