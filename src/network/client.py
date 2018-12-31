""" This module contains a simple implement of Client described in __init__.py"""
import socket


class Client():
    """ A simple client that sends resquest to server and wait for respond """
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port

    def get_data(self, key: str):
        """ Get data from server with respects to the key

        Note that this method will wait until the server respond.

        Args:
            key: the request sent to server

        Returns:
            a bytes array offered by server
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.address, self.port)) # connect to server
        sock.send(key.encode()) # send request (str -> bytes)
        data = sock.recv(32768) # read respond
        while True:
            new_data = sock.recv(32768) # in case the respond is larger than 32768
            if new_data is None or len(new_data) == 0: # if recvive nothing, then break
                break
            data += new_data # append new_data to data
        sock.close() # close connection
        return data
