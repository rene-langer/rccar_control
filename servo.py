import RPi.GPIO as GPIO
import Adafruit_PCA9685
import time
import numpy as np

"""
Version 0.7d -- 10.04.2018
"""
ACCELERATION_CHANNEL = 0
STEERING_CHANNEL = 1

HEADLIGHTS = 10
CURVELIGHT_RIGHT = 9
CURVELIGHT_LEFT = 8

HORN = 11
BACKLIGHTS = 15

BR_LIGHTS_WHITE = 12
BR_LIGHTS_RED = 13

MIDDLE_POSITION = 1500 / 20000


class PwmServo:
    # def __compute_acceleration(self):
    #     x = np.linspace(0, 255, 256)
    #     self.acceleration_values = []
    #
    #     p1 = -9.9343e-10
    #     p2 = 6.4188e-07
    #     p3 = -0.00016455
    #     p4 = 0.020918
    #     p5 = -1.3184
    #     p6 = 33.027
    #
    #     for i in x:
    #         self.acceleration_values.append((8 * i / 255 + 11) / 200)
    #     for i in np.linspace(110, 150, 41):
    #         self.acceleration_values[int(i)] = (p1*i**5 + p2*i**4 + p3*i**3 + p4*i**2 + p5*i + p6)

    def __compute_steering(self):
        x = np.linspace(0, 255, 256)
        self.steering_values = []
        p1 = 9.679e-09
        p2 = -3.7022e-06
        p3 = 0.00047155
        p4 = 0.055
        for i in x:
            self.steering_values.append(p1*i*i*i + p2*i*i + p3*i + p4)

    def __init__(self):

        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.pwm.set_pwm_freq(50)

        self.__compute_steering()
        # self.__compute_acceleration()
        self.back = False
        self.old_back = False
        # set default values
        self.__set_duty_cycle(STEERING_CHANNEL, MIDDLE_POSITION)
        self.__set_duty_cycle(ACCELERATION_CHANNEL, MIDDLE_POSITION)
        self.__lights(0, False, 127)
        self.__horn(0)

    def set_values(self, acceleration, steering, controls):

        if acceleration < 120:
            self.back = True
        else:
            self.back = False

        self.__set_acceleration(acceleration)
        self.__set_steering(steering)

        self.__horn(controls)
        self.__lights(controls, self.back, steering)

    def __set_duty_cycle(self, channel: int, dc: float):
        duty = int(dc*4096)
        self.pwm.set_pwm(channel, 0, duty)

    def __set_acceleration(self, acceleration):
        # PWM for acceleration
        if 115 < acceleration < 140:
            # don´t accelerate
            self.__set_duty_cycle(ACCELERATION_CHANNEL, MIDDLE_POSITION)
        else:
            # accelerate
            self.__set_duty_cycle(ACCELERATION_CHANNEL, (1100+800*(acceleration/255)) / 20000)
            # self.__set_duty_cycle(ACCELERATION_CHANNEL, self.acceleration_values[acceleration])

    def __set_steering(self, control):
        # PWM for controlling
        if 125 < control < 130:
            # don´t control to any side
            self.__set_duty_cycle(STEERING_CHANNEL, MIDDLE_POSITION)
        else:
            # control to any side
            self.__set_duty_cycle(STEERING_CHANNEL, self.steering_values[255-control])

    def __lights(self, other: int, is_reverse: bool, steering: int):
        if other & 128:
            light = True
        else:
            light = False

        if light:
            self.pwm.set_pwm(HEADLIGHTS, 0, 3000)
            self.pwm.set_pwm(BACKLIGHTS, 0, 4000)
            if not is_reverse:
                self.pwm.set_pwm(BR_LIGHTS_RED, 0, 4000)
        else:
            self.pwm.set_pwm(HEADLIGHTS, 0, 0)
            self.pwm.set_pwm(BACKLIGHTS, 0, 0)
            self.pwm.set_pwm(BR_LIGHTS_RED, 0, 0)

        if is_reverse:
            self.pwm.set_pwm(BR_LIGHTS_RED, 0, 0)
            self.pwm.set_pwm(BR_LIGHTS_WHITE, 0, 4000)
        else:
            self.pwm.set_pwm(BR_LIGHTS_WHITE, 0, 0)

        if steering > 140:
            self.pwm.set_pwm(CURVELIGHT_RIGHT, 0, 4000)
            self.pwm.set_pwm(CURVELIGHT_LEFT, 0, 750)
        elif steering < 120:
            self.pwm.set_pwm(CURVELIGHT_LEFT, 0, 4000)
            self.pwm.set_pwm(CURVELIGHT_RIGHT, 0, 750)
        else:
            self.pwm.set_pwm(CURVELIGHT_RIGHT, 0, 750)
            self.pwm.set_pwm(CURVELIGHT_LEFT, 0, 750)

    def __horn(self, other):
        if other & 64:
            self.pwm.set_pwm(HORN, 0, 4090)
        else:
            self.pwm.set_pwm(HORN, 0, 0)
        pass

    def __del__(self):
        self.pwm.set_pwm(CURVELIGHT_LEFT, 0, 0)
        self.pwm.set_pwm(CURVELIGHT_RIGHT, 0, 0)
