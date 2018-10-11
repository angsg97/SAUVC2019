import socket
import threading


class Server(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.waitting_for = None
        self.data = None
        self.data_prepared_event = threading.Event()
        self.stopped = True

    def stop(self):
        self.stopped = True

    def run(self):
        self.stopped = False
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.settimeout(3)
        try:
            server_socket.listen(5)
            while not self.stopped:
                try:
                    sock, addr = server_socket.accept()
                    threading.Thread(target=Server.tcplink,
                                     args=(self, sock, addr)).start()
                except socket.timeout:
                    pass
        finally:
            self.data_prepared_event.set()
            server_socket.close()

    def get_request(self):
        return self.waitting_for

    def offer_data(self, data):
        self.data = data
        self.data_prepared_event.set()
        self.waitting_for = None

    def tcplink(self, sock, _):
        data = sock.recv(128)
        if not data is None and not self.stopped:
            key = bytes.decode(data)
            self.waitting_for = key
            self.data_prepared_event.wait()
            self.data_prepared_event = threading.Event()
            if not data is None:
                sock.send(self.data)
        sock.close()
