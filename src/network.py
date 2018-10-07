import socket
import time
import threading

class Client():

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def get_data(self, key):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.address, self.port))
        s.send(key.encode())
        data = s.recv(4096000)
        s.close()
        return data

class Server(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.waitting_for = None

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', self.port))
        s.listen(5)
        while True:
            sock, addr = s.accept()
            t = threading.Thread(target=Server.tcplink, args=(self, sock, addr))
            t.start()

    def get_request(self):
        return self.waitting_for

    def offer_data(self, key, data):
        self.data = data
        self.data_prepared_event.set()
        self.waitting_for = None

    def tcplink(self, sock, addr):
        data = sock.recv(128)
        if not data is None:
            key = bytes.decode(data)
            self.waitting_for = key
            self.data_prepared_event = threading.Event()
            self.data_prepared_event.wait()
            sock.send(self.data)
            self.data = None
        sock.close()
