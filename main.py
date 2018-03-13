import Draft_0_6.servo as servo
import Draft_0_6.server as server

import time

"""
CHANGELOG:

#1: Removed 1 second delay before sending SERVER_CONNECTION_CLOSED at disconnect
#2: Edited constant byte values to server constants. See #1 in server class
"""


def debug_print(message: str, mode: bool):
    if mode:
        print(message)


if __name__ == '__main__':
    IP_ADDRESS = "192.168.4.1"
    DEBUG = False

    start_time = time.time()

    print("##########################################################\n"
          "### RC-Car\n"
          "### Server Version 0.6.1 - Expecting client version 0.6\n"
          "### Server is going to be hosted on {}\n".format(IP_ADDRESS) +
          "### ")

    servo_control = servo.Servo()
    server = server.Server(IP_ADDRESS, 9999)

    print("### Initialization finished in {:1.4f} seconds".format((time.time()-start_time)))
    print("##########################################################\n\n")
    while not server.termination_pending:
        print("\tWaiting for incoming connection...")

        (conn, (ip, port)) = server.accept()

        session_active = True
        print("\tAccepted connection from {}:{}".format(ip, port))

        while session_active:
            # receive a maximum of 1 byte for data type
            data_type = conn.recv(1)

            if data_type == server.SERVER_REQUEST:
                conn.send(server.SERVER_READY)

                # receive 3-byte data frame
                data = conn.recv(3)

                servo_control.set_values(data[0], data[1], data[2])

                # if last bit of byte 3 is set cancel connection
                if data[2] & 1 == 1:
                    session_active = False
                    print("\nSession is going to be terminated.")
                    conn.send(server.SERVER_CONNECTION_CLOSED)
                    time.sleep()

                # if second-last bit of byte 3 is set,
                # terminate communication and server
                if data[2] & 2 == 2:
                    print("\nTerminating session and shutting down server application")
                    session_active = False
                    server.termination_pending = True
                    conn.send(server.SERVER_CONNECTION_CLOSED)

                else:
                    # send done code 0x12
                    print("Data: 0x{0:x};0x{1:x};0x{2:x}\r".format(data[0], data[1], data[2]), end="", flush=True)
                    conn.send(server.SERVER_FINISHED)

            else:
                # not known, do nothing
                pass

    server.__del__()
    print("Server closed.")