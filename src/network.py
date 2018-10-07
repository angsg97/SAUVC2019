import socket
import threading

class Client():

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def get_data(self, key):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.address, self.port))
        s.send(key.encode())
        data = s.recv(4096)
        while True:
            new_data = s.recv(32768)
            if new_data is None or len(new_data) == 0:
                break
            data += new_data
        s.close()
        return data

class Server(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.waitting_for = None
        self.data = None
        self.data_prepared_event = None
        self.stopped = True

    def stop(self):
        self.stopped = True

    def run(self):
        self.stopped = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', self.port))
        sock.settimeout(3)
        sock.listen(5)
        while not self.stopped:
            try:
                sock, addr = sock.accept()
                threading.Thread(target=Server.tcplink, args=(self, sock, addr)).start()
            except socket.timeout:
                pass
        sock.close()
        print("Server thread exited")

    def get_request(self):
        return self.waitting_for

    def offer_data(self, data):
        self.data = data
        self.data_prepared_event.set()
        self.waitting_for = None

    def tcplink(self, sock, _):
        data = sock.recv(128)
        if not data is None:
            key = bytes.decode(data)
            self.waitting_for = key
            self.data_prepared_event = threading.Event()
            self.data_prepared_event.wait()
            sock.send(self.data)
            self.data = None
        sock.close()
