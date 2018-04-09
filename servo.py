import RPi.GPIO as GPIO
import Adafruit_PCA9685

"""
Version 0.6

CHANGELOG
#1: Added setwarnings(False) in first line of init() to supress 'Pin already used' on startup
"""


class PwmServo:
    def __init__(self):
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.pwm.set_pwm_freq(50)

        # set default value 1.5ms
        self.pwm.set_pwm(0, 0, 50 * 0.0015 * 4096)
        self.pwm.set_pwm(1, 0, 50 * 0.0015 * 4096)

    def set_values(self, acceleration, steering, controls):
        self.__set_acceleration(acceleration)
        self.__set_steering(steering)
        self.__horn(controls)
        self.__lights(controls, steering)

    def __set_on_time(self, channel: int, on_time_us: int):
        on_clockcycles =  4096 * (on_time_us / 20000)
        self.pwm.set_pwm(channel, 0, on_clockcycles)

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