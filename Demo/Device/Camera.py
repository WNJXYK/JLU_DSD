import socket
from multiprocessing import Manager
from threading import Thread
import json, time

manager = Manager()
camera_state = manager.Value('b', False)
camera_change = manager.Value('i', 0)


def detected():
    global camera_state, camera_change
    camera_state.value = not camera_state.value
    camera_change.value = camera_change.value + 1


def report_socket(SERVER_ADDRESS, id, type):
    global camera_state, camera_change
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
            camera_change.value = 1


            # Solve
            while True:
                if camera_change.value > 0:
                    socket_out.send(('{"data":"%s"}'%str(camera_state.value)).encode("utf8"))
                    camera_change.value = 0
                time.sleep(0.1)

        except: pass
        finally:
            # Wait & Reconnect
            socket_out.close()
            print("Server Error(Reporter) : Wait 5s & Reconnecting...")
            time.sleep(5)

def main():
    SERVER_ADDRESS = ('127.0.0.1', 1033)

    report = Thread(target=report_socket, args=(SERVER_ADDRESS, "popoqqq", "Camera", ))
    report.setDaemon(True)
    report.start()

    while True:
        input()
        detected()
        time.sleep(1)

if __name__ == '__main__': main()

