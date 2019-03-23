
cnt = 0
def Run(info):
    global cnt
    print(info)
    cnt = cnt+1
    if cnt%2 == 0: return '{"data":"on"}'
    return '{"data":"off"}'

def Cmd(info):
    print(info)
    return '{"data":"%s"}'%info["cmd"]