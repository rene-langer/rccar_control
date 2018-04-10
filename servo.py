import RPi.GPIO as GPIO
import Adafruit_PCA9685

"""
Version 0.6

CHANGELOG
#1: Added setwarnings(False) in first line of init() to suppress 'Pin already used' on startup
"""


class PwmServo:
    def __init__(self):

        GPIO.setwarnings(False)
        GPIO.cleanup()
        
        # Rename Pins
        self.lightPin = 18
        self.corneringRight = 11
        self.corneringLeft = 13
        self.horn = 12

        GPIO.setmode(GPIO.BOARD)

        # Define light pins
        GPIO.setup(self.lightPin, GPIO.OUT)
        GPIO.setup(self.corneringRight, GPIO.OUT)
        GPIO.setup(self.corneringLeft, GPIO.OUT)
        GPIO.setup(self.horn, GPIO.OUT)

        GPIO.output(self.lightPin, GPIO.HIGH)
        GPIO.output(self.corneringRight, GPIO.HIGH)
        GPIO.output(self.corneringLeft, GPIO.HIGH)
        GPIO.output(self.horn, GPIO.HIGH)

        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.pwm.set_pwm_freq(50)

        # set default value 1.5ms
        self.pwm.set_pwm(0, 0, int(50 * 0.0015 * 4096))
        self.pwm.set_pwm(1, 0, int(50 * 0.0015 * 4096))

    def set_values(self, acceleration, steering, controls):
        self.__set_acceleration(acceleration)
        self.__set_steering(steering)
        self.__horn(controls)
        self.__lights(controls, steering)

    def __set_on_time(self, channel: int, on_time_us: int):
        on_clockcycles = 4096 * (on_time_us / 20000)
        self.pwm.set_pwm(channel, 0, int(on_clockcycles))

    def __set_acceleration(self, acceleration):
        # PWM for acceleration
        if 125 < acceleration < 130:
            # don´t accelerate
            self.__set_on_time(0, 1500)
        else:
            # accelerate
            self.__set_on_time(0, 1100+800*(acceleration/255))

    def __set_steering(self, control):
        # PWM for controlling
        if 125 < control < 130:
            # don´t control to any side
            self.__set_on_time(1, 1500)
        else:
            # control to any side
            self.__set_on_time(1, 1100 + 800*(255-control)/255)

    def __lights(self, other, control):
        if other & 128:
            GPIO.output(self.lightPin, GPIO.LOW)
            if control > 190:
                GPIO.output(self.corneringRight, GPIO.LOW)
                GPIO.output(self.corneringLeft, GPIO.HIGH)
            elif control < 65:
                GPIO.output(self.corneringRight, GPIO.HIGH)
                GPIO.output(self.corneringLeft, GPIO.LOW)
            else:
                GPIO.output(self.corneringRight, GPIO.HIGH)
                GPIO.output(self.corneringLeft, GPIO.HIGH)
        else:
            GPIO.output(self.lightPin, GPIO.HIGH)
            GPIO.output(self.corneringRight, GPIO.HIGH)
            GPIO.output(self.corneringLeft, GPIO.HIGH)

    def __horn(self, other):
        if other & 64:
            GPIO.output(self.horn, GPIO.LOW)
        else:
            GPIO.output(self.horn, GPIO.HIGH)

    def __del__(self):
        GPIO.cleanup()


class Servo:

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.cleanup()
        # Rename Pins
        self.accelerationPin = 15
        self.controlPin = 16
        self.lightPin = 18
        self.corneringRight = 11
        self.corneringLeft = 13
        self.horn = 12

        GPIO.setmode(GPIO.BOARD)

        # Define Pin 22 and 23 as output
        GPIO.setup(self.accelerationPin, GPIO.OUT)
        GPIO.setup(self.controlPin, GPIO.OUT)
        # Define light pins
        GPIO.setup(self.lightPin, GPIO.OUT)
        GPIO.setup(self.corneringRight, GPIO.OUT)
        GPIO.setup(self.corneringLeft, GPIO.OUT)
        GPIO.setup(self.horn, GPIO.OUT)

        self.acc = GPIO.PWM(self.accelerationPin, 50)
        self.acc.start(1.5/20*100)

        self.con = GPIO.PWM(self.controlPin, 50)
        self.con.start(1.5/20*100)

        GPIO.output(self.lightPin, GPIO.HIGH)
        GPIO.output(self.corneringRight, GPIO.HIGH)
        GPIO.output(self.corneringLeft, GPIO.HIGH)
        GPIO.output(self.horn, GPIO.HIGH)

    def set_values(self, acceleration, steering, controls):
        self.__set_acceleration(acceleration)
        self.__set_steering(steering)
        self.__horn(controls)
        self.__lights(controls, steering)

    def __set_acceleration(self, acceleration):
        # PWM for acceleration
        if 125 < acceleration < 130:
            # don´t accelerate
            self.acc.ChangeDutyCycle(1.5/20*100)
        else:
            # accelerate
            self.acc.ChangeDutyCycle((1.1+0.8*(acceleration/255))/20*100)

    def __set_steering(self, control):
        # PWM for controlling
        if 125 < control < 130:
            # don´t control to any side
            self.con.ChangeDutyCycle(1.5 / 20 * 100)
        else:
            # control to any side
            self.con.ChangeDutyCycle((1.1+0.8*((255-control)/255))/20*100)

    def __lights(self, other, control):
        if other & 128:
            GPIO.output(self.lightPin, GPIO.LOW)
            if control > 190:
                GPIO.output(self.corneringRight, GPIO.LOW)
                GPIO.output(self.corneringLeft, GPIO.HIGH)
            elif control < 65:
                GPIO.output(self.corneringRight, GPIO.HIGH)
                GPIO.output(self.corneringLeft, GPIO.LOW)
            else:
                GPIO.output(self.corneringRight, GPIO.HIGH)
                GPIO.output(self.corneringLeft, GPIO.HIGH)
        else:
            GPIO.output(self.lightPin, GPIO.HIGH)
            GPIO.output(self.corneringRight, GPIO.HIGH)
            GPIO.output(self.corneringLeft, GPIO.HIGH)

    def __horn(self, other):
        if other & 64:
            GPIO.output(self.horn, GPIO.LOW)
        else:
            GPIO.output(self.horn, GPIO.HIGH)

    def __del__(self):
        GPIO.cleanup()