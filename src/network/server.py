import socket
import threading


class Server(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.waitting_for = {}
        self.data = None
        self.data_prepared_event = threading.Event()
        self.stopped = True

    def stop(self):
        self.stopped = True

    def run(self):
        self.stopped = False
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow the port be reused after closing
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.settimeout(3)
        try:
            server_socket.listen(5)
            while not self.stopped:
                try:
                    sock, _ = server_socket.accept()
                    threading.Thread(target=Server.tcplink,
                                     args=(self, sock)).start()
                except socket.timeout:
                    pass
        finally:
            self.data_prepared_event.set()
            server_socket.shutdown(socket.SHUT_RDWR)
            server_socket.close()

    def get_requests(self):
        return self.waitting_for.keys()

    def offer_data(self, key, data):
        self.waitting_for[key] = data
        self.data_prepared_event.set()
        self.data_prepared_event = threading.Event()

    def tcplink(self, sock):
        recv = sock.recv(128)
        if not recv is None and not self.stopped:
            key = bytes.decode(recv)
            self.waitting_for[key] = None
            while True:
                self.data_prepared_event.wait()
                if not self.waitting_for[key] is None:
                    sock.send(self.waitting_for[key])
                    break
        sock.close()
