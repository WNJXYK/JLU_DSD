from Server.Database import IDatabase
import json, uuid


def login_user(user, password):
    _, id = IDatabase.render("SELECT id FROM User WHERE user = ? and password = ?", (user, password, ))
    if len(id) == 0: return 1, "Wrong User or Password", {}

    token = str(uuid.uuid4())
    IDatabase.render("UPDATE User SET token = ? WHERE user = ?", (token, user, ))

    _, _, user = query_user(id[0][0])
    user["token"] = token

    return 0, "", user


def add_user(user, name, password, role):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Role WHERE id = ?", (role, ))
    if cnt[0][0] == 0: return 1, "No Such Role"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM User WHERE user = ?", (user,))
    if cnt[0][0] > 0: return 2, "User is Existed"

    IDatabase.render("INSERT INTO User (user, name, password, role, permission, token) VALUES ('%s', '%s', '%s', %d, '%s', '%s')" % (user, name, password, role, json.dumps({}), str(uuid.uuid4())))
    return 0, ""


def del_user(id):
    if int(id) == 1: return 1, "Can not delete Admin"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM User WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 2, "No Such User"

    IDatabase.render("DELETE FROM User WHERE id = ?", (id, ))
    return 0, ""


def list_user():
    _, user = IDatabase.render("SELECT id FROM User")

    ret = []
    for u in user: ret.append(query_user(u[0])[2])

    return 0, "", ret


def modify_user(id, name, role, permission):
    if int(id) == 1: return 1, "Can not modify Admin"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM User WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such User"

    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Role WHERE id = ?", (role,))
    if cnt[0][0] == 0: return 2, "No Such Role"

    try:
        p_json = json.loads(permission)
    except Exception as errr:
        return 3, "Error Permission Json"

    IDatabase.render("UPDATE User SET role = ?, name = ?, permission = ? WHERE id = ?", (role, name, permission, id, ))
    return 0, ""


def query_user(id):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM User WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such User", {}

    _, user = IDatabase.render("SELECT user, name, role, permission FROM User WHERE id = ?", (id, ))
    name, role_id, permission = user[0][1], user[0][2], user[0][3]
    user = user[0][0]

    _, role = IDatabase.render("SELECT name, priority, permission  FROM Role WHERE id = ?", (role_id, ))
    role_name, priority, role_permission = role[0][0], role[0][1], role[0][2]

    role_permission = json.loads(role_permission)
    user_permission = json.loads(permission)
    permission_str = []
    for p in role_permission:
        if int(role_permission[p]) == 1 and (p not in user_permission or int(user_permission[p]) == 1):
            permission_str.append(p)
    for p in user_permission:
        if int(user_permission[p]) == 1 and (p not in permission_str):
            permission_str.append(p)

    ret = {"id": id, "user": user, "name": name, "role": role_name, "priority": priority, "permission": permission, "permission_str": permission_str}
    return 0, "", ret


def modify_role(id, priority):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM Role WHERE id = ?", (id,))
    if cnt[0][0] == 0: return 1, "No Such Role"

    try:
        p = int(priority)
        if not 0 < p < 100 :
            raise BaseException
    except:
        return 2, "Priority should in range [1, 100)"

    IDatabase.render("UPDATE Role SET priority = ? WHERE id = ?", (priority, id, ))
    return 0, ""


def query_permission(id, token, op):
    _, cnt = IDatabase.render("SELECT COUNT(*) FROM User WHERE id = ?", (id,))
    if cnt[0][0] == 0: return False
    _, user = IDatabase.render("SELECT role, permission, token FROM User WHERE id = ?", (id, ))
    role_id, permission, tk = user[0][0], user[0][1], user[0][2]

    if tk != token: return False
    if len(op) <= 0: return True

    _, role = IDatabase.render("SELECT permission FROM Role WHERE id = ?", (role_id, ))
    role_permission = role[0][0]

    permission = json.loads(permission)
    role_permission = json.loads(role_permission)

    if (op not in role_permission) and (op not in permission): return False

    if op in permission: return permission[op] == 1
    if op in role_permission: return role_permission[op] == 1


def query_role():
    _, role = IDatabase.render("SELECT id, name, priority, permission FROM Role")

    ret = []
    for r in role:
        permission_str = []
        role_permission = json.loads(r[3])
        for p in role_permission:
            if int(role_permission[p]) == 1:
                permission_str.append(p)
        ret.append({"id": r[0], "name": r[1], "priority":r[2], "permission": r[3], "permission_str": permission_str})

    return 0, "", ret

