import socket


class Client():

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def get_data(self, key):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.address, self.port))
        s.send(key.encode())
        data = s.recv(32768)
        while True:
            new_data = s.recv(32768)
            if new_data is None or len(new_data) == 0:
                break
            data += new_data
        s.close()
        return data
