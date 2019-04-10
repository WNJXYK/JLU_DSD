
class Controller(object):
    def __init__(self):
        self.cnt = 0

    def Run(self, info):
        if len(info["sensors"]) <= 0: return '{"data":"off"}'
        # print(info["sensors"][0])
        # self.cnt = self.cnt+1
        sensors = info["sensors"][0]
        if ('data' in sensors) and (sensors["data"] == 'True'): return '{"data":"on"}'
        return '{"data":"off"}'

    def Cmd(self, info):
        #print(info)
        return '{"data":"%s"}'%info["cmd"]
