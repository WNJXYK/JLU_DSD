from collections import deque

ONLINE_THRESHOLD = 10
HEART_BEAT = 1
CONTROLLER_ADDRESS_NAME = "Controller_Address"
LAST_COMMAND = deque(maxlen=30)