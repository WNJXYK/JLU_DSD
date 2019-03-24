import time
from Demo.Hardware.Hardware import Hardware

light = Hardware(('127.0.0.1', 1024), "qwerty", "LightDevice", "Auth")


def package_data():
    return '{"data":"%s"}' % str(light.value)

def receive_cmd(cmd):
    goal = None
    if cmd['data'] == 'on':
        print("Light : On")
        goal = True
    if cmd['data'] == 'off':
        print("Light : Off")
        goal = False

    if (goal is not None) and light.value.value != goal:
        light.value.value = goal
        light.change.value = True
    else:
        light.change.value = False

def main():
    light.receive(receive_cmd)
    light.report(package_data)

    while True:
        input()
        light.value.value = not light.value.value
        light.change.value = True
        time.sleep(1)

if __name__ == '__main__': main()