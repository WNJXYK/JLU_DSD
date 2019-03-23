import socket
from multiprocessing import Manager
from threading import Thread
import json, time

manager = Manager()
light_state = manager.Value('b', False)
light_change = manager.Value('i', 0)

# Be Controlled Physically
def physics():
    global light_state, light_change
    light_state.value = not light_state.value
    light_change.value = light_change.value + 1


# Report State
def report_socket(SERVER_ADDRESS, id, type):
    global light_state, light_change
    while True:
        try:
            # Connect & Hello
            socket_out = socket.socket()
            socket_out.connect(SERVER_ADDRESS)
            socket_out.send(('{"id":"%s", "type":"%s", "socket":"in", "auth":"Auth"}'%(id, type)).encode("utf8"))

            # Hello
            hello = json.loads(socket_out.recv(1024))
            if int(hello["status"]) != 0:
                print("Server Error(Reporter) : %s" % hello["msg"])
                continue
            else:
                print("Server Error(Reporter) : Connected")
            light_change.value = 1

            # Solve
            while True:
                if light_change.value > 0:
                    socket_out.send(('{"data":"%s"}'%str(light_state.value)).encode("utf8"))
                    light_change.value = 0
                time.sleep(0.5)

        except: pass
        finally:
            # Wait & Reconnect
            socket_out.close()
            print("Server Error(Reporter) : Wait 5s & Reconnecting...")
            time.sleep(5)


# Receive Command
def receive_socket(SERVER_ADDRESS, id, type):
    global light_state, light_change
    while True:
        try:
            # Connect
            socket_in = socket.socket()
            socket_in.connect(SERVER_ADDRESS)
            socket_in.send(('{"id":"%s", "type":"%s", "socket":"out", "auth":"Auth"}' % (id, type)).encode("utf8"))

            # Hello
            hello = json.loads(socket_in.recv(1024))
            if int(hello["status"]) != 0:
                print("Server Error(Receiver) : %s"%hello["msg"])
                continue
            else: print("Server Error(Receiver) : Connected")

            # Solve
            while True:
                try:
                    cmd = socket_in.recv(1024)
                    if len(cmd) == 0 : break
                    cmd = json.loads(cmd)
                    if cmd['data'] == 'on':
                        print("Light : On")
                        light_state.value = True
                        light_change.value = 0
                    if cmd['data'] == 'off':
                        print("Light : Off")
                        light_state.value = False
                        light_change.value = 0
                except: print("Command Error : %s\n" % cmd)

        except: pass
        finally:
            # Wait & Reconnect
            socket_in.close()
            print("Server Error(Receiver) : Wait 5s & Reconnecting...")
            time.sleep(5)


def main():
    SERVER_ADDRESS = ('127.0.0.1', 1033)

    receive = Thread(target=receive_socket, args=(SERVER_ADDRESS, "qwerty", "LightDevice", ))
    receive.setDaemon(True)
    receive.start()

    report = Thread(target=report_socket, args=(SERVER_ADDRESS, "qwerty", "LightDevice", ))
    report.setDaemon(True)
    report.start()

    while True:
        input()
        physics()
        time.sleep(1)

if __name__ == '__main__': main()

