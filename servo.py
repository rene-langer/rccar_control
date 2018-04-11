import RPi.GPIO as GPIO
import Adafruit_PCA9685
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

        # set default values
        self.__set_duty_cycle(STEERING_CHANNEL, MIDDLE_POSITION)
        self.__set_duty_cycle(ACCELERATION_CHANNEL, MIDDLE_POSITION)
        self.old_controls = 0
        self.__lights(self.old_controls, False, 127)
        self.__horn(self.old_controls)

    def set_values(self, acceleration, steering, controls):
        self.__set_acceleration(acceleration)
        self.__set_steering(steering)
        if acceleration < 120:
            back = True
        else:
            back = False

        self.__horn(controls)
        self.__lights(controls, back, steering)

    def __set_on_time(self, channel: int, on_time_us: int):
        on_clockcycles = 4096 * (on_time_us / 20000)
        self.pwm.set_pwm(channel, 0, int(on_clockcycles))

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
            self.pwm.set_pwm(HEADLIGHTS, 0, 4000)
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
