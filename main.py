import servo
import server

import time

"""
CHANGELOG:

#1: Removed 1 second delay before sending SERVER_CONNECTION_CLOSED at disconnect
#2: Edited constant byte values to server constants. See #1 in server class
"""

if __name__ == '__main__':
    IP_ADDRESS = "192.168.4.1"
    DEBUG = False

    start_time = time.time()

    print("##########################################################\n"
          "### RC-Car\n"
          "### Server Version 0.6.1 - Expecting client version 0.6\n"
          "### Server is going to be hosted on {}\n".format(IP_ADDRESS) +
          "### ")

    #servo_control = servo.Servo()
    servo_control = servo.PwmServo()
    server = server.Server(IP_ADDRESS, 9999)

    print("### Initialization finished in {:1.4f} seconds".format((time.time()-start_time)))
    print("##########################################################\n\n")
    while not server.termination_pending:
        print("\tWaiting for incoming connection...")

        # wait until a connection is established
        server.await_connection()

        while server.connection_active:

            data_type = server.receive()

            if len(data_type) == 1 and data_type == server.SERVER_REQUEST:
                server.send_byte(server.SERVER_READY)

                # receive 3-byte data frame
                data = server.receive()

                if len(data) == 3:
                    servo_control.set_values(data[0], data[1], data[2])
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
                    print("\t\tData: 0x{0:x};0x{1:x};0x{2:x}\r".format(data[0], data[1], data[2]), end="", flush=True)
                    server.send_byte(server.SERVER_FINISHED)

            else:
                print("Unexpected Type:{} \r".format(data_type))

    server.__del__()
    print("Server closed.")
