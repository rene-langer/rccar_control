import subprocess
import RPi.GPIO as GPIO
from subprocess import check_output
import threading

import sys, os
import time

frontSwitch = 38
backSwitch = 36
firstClick = True

GPIO.setmode(GPIO.BOARD)
GPIO.setup(frontSwitch, GPIO.IN)
GPIO.setup(backSwitch, GPIO.IN)

def start():
    serverInstance = subprocess.call("python3 " + path + "/main.py", shell=True)


if __name__ == '__main__':
    while True:
        if GPIO.input(frontSwitch) == GPIO.HIGH:
            if firstClick:
                path = os.path.dirname(sys.argv[0])
                server = threading.Thread(name="start", target=start).start()
                firstClick = False
        if GPIO.input(backSwitch) == GPIO.HIGH:
            x = check_output(["pidof", "python3"])
            x = x.split(b' ')[0]
            x = int(x.decode("utf-8"))
            print(x)
            if not firstClick:
                os.system('kill ' + str(x))
                firstClick = True