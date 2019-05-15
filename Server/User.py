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
        :param uid: 用户ID / User ID
        :param key: 关键字 / Key
        :param value: 数据 / Data
        '''
        if uid not in self.data: self.data[uid] = {}
        info = self.data[uid]
        info[key] = value
        self.data[uid] = info

    def get(self, uid):
        '''
        获得用户数据 / Get user data
        :param hid: 用户ID / User ID
        :return: 用户数据 / User data
        '''
        return self.data[uid]

    def check(self, uid, sid):
        '''
        检查用户有效性 / Check user's validation
        :param hid: 用户ID / User ID
        :param sid: 用户令牌 / Security Toekn
        :return: 用户数据 / User data
        '''
        if uid not in self.data: return False
        if self.get(uid)["SID"] != sid: return False
        if time.time()-self.get(uid)["Last"] > 7*24*60*60: return False
        return True

    def update(self, uid):
        '''
        更新用户时间戳 / 更新用户时间戳
        :param hid: 用户ID / User ID
        '''
        self.modify(uid, "Last", time.time())

    def allocate(self, uid, nick, auth):
        '''
        分配用户安全令牌 / Allocate User's Security Token
        :param uid: 用户ID / User ID
        :param nick: 用户名 / Nickname
        :param auth 
        :return: sid: 用户令牌 / Security Token
        '''
        self.modify(uid, "Last", time.time())
        self.modify(uid, "Nickname", nick)
        self.modify(uid, "Role", int(auth))
        self.modify(uid, "Admin", (1 if int(auth) >= 3 else 0))
        sid = str(uuid.uuid4())
        self.modify(uid, "SID", sid)
        return sid



