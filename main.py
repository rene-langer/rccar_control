import servo
import server
import RPi.GPIO as GPIO

import time, threading


class TPSCounter(object):
    def __init__(self, servos: servo.PwmServo):
        self.last_second = 0
        self.current = 0
        self.servo = servos

    def inc(self):
        self.current += 1

    def __check(self):
        if self.last_second < 5:
            self.servo.set_values(127, 127, 0)

    def __reset(self):
        self.current = 0

    def _run(self):
        self.last_second = self.current
        self.__reset()
        self.__check()
        threading.Timer(1.0, self._run).start()

    def start(self):
        threading.Timer(1.0, self._run).start()


if __name__ == '__main__':
    IP_ADDRESS = "192.168.5.1"

    start_time = time.time()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(21, GPIO.OUT)
    led = GPIO.PWM(21, 2)

    led.start(0.5)

    print("##########################################################\n"
          "### RC-Car\n"
          "### Server Version 0.7.1b - Expecting client version 0.7b\n"
          "### Server is going to be hosted on {}\n".format(IP_ADDRESS) +
          "###")

    servo_control = servo.PwmServo()
    server = server.Server(IP_ADDRESS, 9999)

    tps = TPSCounter(servo_control)
    tps.start()

    print("### Initialization finished in {:1.4f} seconds".format((time.time()-start_time)))
    print("##########################################################\n\n")
    while not server.termination_pending:
        print("\tWaiting for incoming connection...")
        led.ChangeDutyCycle(0.5)

        # wait until a connection is established
        server.await_connection()

        while server.connection_active:
            led.ChangeDutyCycle(0)
            data_type = server.receive()

            if len(data_type) == 1 and data_type == server.SERVER_REQUEST:
                server.send_byte(server.SERVER_READY)

                # receive 3-byte data frame
                data = server.receive()

                if len(data) == 3:
                    servo_control.set_values(data[0], data[1], data[2])
                    tps.inc()

                else:
                    continue

                # if last bit of byte 3 is set cancel connection
                if data[2] & 1 == 1:
                    print("\nSession is going to be terminated.")
                    server.send_byte(server.SERVER_CONNECTION_CLOSED)
                    time.sleep(0.2)
                    server.close_connection()

                # if second-last bit of byte 3 is set,
                # terminate communication and serve
                elif data[2] & 2 == 2:
                    print("\nTerminating session and shutting down server application")
                    server.termination_pending = True
                    server.send_byte(server.SERVER_CONNECTION_CLOSED)
                    server.close_connection()

                else:
                    # send done code 0x12
                    print("TPS:{3}\tData: 0x{0:x};0x{1:x};0x{2:x}\r".format(data[0], data[1], data[2], tps.last_second)
                          , end="", flush=True)
                    server.send_byte(server.SERVER_FINISHED)

            elif len(data_type) == 1 and data_type == server.SERVER_BATTERY_REQUEST:
                # put battery request handler here
                pass

            else:
                print("Unexpected Type:{} \r".format(data_type))

    server.__del__()
    print("Server closed.")
