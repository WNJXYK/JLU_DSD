import time, uuid

class User(object):
    '''
    服务器用户类：管理用户身份
    User Class: Manage User's Identify
    '''
    def __init__(self, manager):
        self.data = manager.dict()

    def modify(self, uid, key, value):
        '''
        修改用户数据 / Modify user data
        :param uid: 硬件ID / User ID
        :param value: 数据 / Data
        '''
        if uid not in self.data: self.data[uid] = {}
        info = self.data[uid]
        info[key] = value
        self.data[uid] = info

    def get(self, uid):
        '''
        获得用户数据 / Get user data
        :param hid: 硬件ID / User ID
        :return: 硬件数据 / User data
        '''
        return self.data[uid]

    def check(self, uid, sid):
        if uid not in self.data: return False
        if self.get(uid)["SID"] != sid: return False
        if time.time()-self.get(uid)["Last"] > 7*24*60*60: return False
        return True

    def update(self, uid):
        self.modify(uid, "Last", time.time())

    def allocate(self, uid, nick, auth):
        self.modify(uid, "Last", time.time())
        self.modify(uid, "Nickname", nick)
        self.modify(uid, "Authority", int(auth))
        self.modify(uid, "Admin", (1 if int(auth) >= 3 else 0))
        sid = str(uuid.uuid4())
        self.modify(uid, "SID", sid)
        return sid



