
class Controller(object):
    def __init__(self):
        self.cnt = 0

    def Run(self, info):
        # print(info)
        self.cnt = self.cnt+1
        if self.cnt%2 == 0: return '{"data":"on"}'
        return '{"data":"off"}'

    def Cmd(self, info):
        #print(info)
        return '{"data":"%s"}'%info["cmd"]
