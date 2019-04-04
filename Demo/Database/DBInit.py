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
           SensorCNT INTEGER NOT NULL,
           DeviceCNT INTEGER NOT NULL,
           Details TEXT);
           ''')

    # Add Init Info
    c.execute("INSERT INTO Room (Nickname, SensorCNT, DeviceCNT) \
            VALUES ('Zero', 0, 1)")
    c.execute("INSERT INTO Room (Nickname, SensorCNT, DeviceCNT) \
                VALUES ('NULL', 0, 0)")
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
    c.execute("INSERT INTO Hardware (HID, Nickname, Type, Ctrl) \
                VALUES ('Raspi', '测试小灯', 'Light', 1)")
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
    c.execute("INSERT INTO rUser (RID, UID) \
                VALUES (1, 2)")
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
    c.execute("INSERT INTO rHardware (HID, RID) \
                VALUES ('Raspi', 1)")
    conn.commit()

    conn.close()