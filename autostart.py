import subprocess
import RPi.GPIO as GPIO

frontSwitch = 38
backSwitch = 36
firstClick = 1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(frontSwitch, GPIO.IN)
GPIO.setup(backSwitch, GPIO.IN)

if GPIO.input(frontSwitch):
    if firstClick:
        serverStart = subprocess.Popen(["./server.py"])
        firstClick = 0
    else:
        serverStart = subprocess.Pclose(["./server.py"])
        serverStart = subprocess.Popen(["./server.py"])
