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

        self.conn = None
        self.client_ip = None
        self.client_port = None
        self.connection_active = False

        # only accept one connection at a time
        self.listen(1)

        self.termination_pending = False

    def send_byte(self, byte):
        self.conn.send(byte)

    def receive(self):
        data = self.conn.recv(8)

        return data

    def await_connection(self):
        if not self.connection_active:
            (self.conn, (self.client_ip, self.client_port)) = self.accept()
            print("\tAccepted connection from {}:{}".format(self.client_ip, self.client_port))
            self.connection_active = True
        else:
            print("E: Cannot accept connection due another connection is still active")

    def close_connection(self):
        if self.connection_active:
            self.conn = None
            self.client_ip = None
            self.client_port = None
            self.connection_active = False
            print("Connection to client closed")
        else:
            print("E: Could not close connection: No connection established. !!!")

    def __del__(self):
        self.close()
