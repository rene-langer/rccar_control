import socket
import time

"""
TCPSocket Server: Version 1.0
09.03.2018

CHANGELOG:
#1: Added Byte constants according to TCPCommands.java
"""


class Server(socket.socket):

    SERVER_CONNECTION_CLOSED = b'\x13'
    SERVER_REQUEST = b'\x01'
    SERVER_READY = b'\x11'
    SERVER_FINISHED = b'\x12'

    def __init__(self, host: str, port: int):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind_error = True
        self.first_error = True

        while self.bind_error:
            try:
                self.bind((host, port))

                self.running = True
                print("### Listening on {0}:{1}".format(host, port))
                self.bind_error = False

            except OSError:
                if self.first_error:
                    print("### Cannot bind server instance. Address may be used by other instance.\n"
                          "### Waiting for Port to timeout...\n")
                    self.first_error = False
                else:
                    pass
                self.running = False
                time.sleep(1)

        # only accept one connection at a time
        self.listen(1)

        self.termination_pending = False

    def __del__(self):
        self.close()
