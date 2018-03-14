import servo
import server

import time

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

        # wait until a connection is established
        server.await_connection()

        while server.connection_active:
            # receive data request
            data_type = server.receive()

            # expected SERVER_REQUEST; size needs to be 1 byte
            if len(data_type) == 1 and data_type == server.SERVER_REQUEST:
                server.send_byte(server.SERVER_READY)

                # receive data frame
                data = server.receive()

                if len(data) == 3:
                    servo_control.set_values(data[0], data[1], data[2])
                else:
                    # error in incoming data; start next loop cycle
                    continue

                # check byte 3 bit 2^0: terminate session if set
                if data[2] & 1 == 1:
                    print("\nSession is going to be terminated.")
                    server.send_byte(server.SERVER_CONNECTION_CLOSED)
                    time.sleep(0.2)
                    server.close_connection()

                # check byte 3 bit 2^1: terminate session and server if set
                if data[2] & 2 == 2:
                    print("\nTerminating session and shutting down server application")
                    server.termination_pending = True
                    server.send_byte(server.SERVER_CONNECTION_CLOSED)
                    server.close_connection()

                # no exit bit set, so send SERVER_FINISHED
                else:
                    # send done code 0x12
                    print("Data: 0x{0:x};0x{1:x};0x{2:x}\r".format(data[0], data[1], data[2]), end="", flush=True)
                    server.send_byte(server.SERVER_FINISHED)

            else:
                # unknown data type, do nothing
                pass

    # unbind server and close application
    server.__del__()
    print("Server closed.")
