""" This module contains a simple implement of Server described in __init__.py"""
import socket
import threading


class Server(threading.Thread):
    """ A simple implement of Server """

    def __init__(self, port: int):
        """ Create an instance of Server
        The server will not start until start() is called
        """
        threading.Thread.__init__(self)
        self.port = port
        self.waitting_for = {}
        self.data = None
        self.data_prepared_event = threading.Event()
        self.stopped = True

    def stop(self):
        """ Stop server
        (It may not stop immediately)
        """
        self.stopped = True

    def run(self):
        """ Main thread for server """
        self.stopped = False
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # allow the port be reused after closing
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.port)) # bind the server to the port
        server_socket.settimeout(3)
        server_used = False
        try:
            server_socket.listen(5) # start listening
            while not self.stopped:
                try:
                    sock, _ = server_socket.accept() # wait for new connection
                    server_used = True
                    # start a tcp link thread and pass the connected socket to it
                    # and the new thread will handle the request
                    threading.Thread(target=Server.__tcp_link,
                                     args=(self, sock)).start()
                except socket.timeout:
                    pass
        # stop the server
        finally:
            self.data_prepared_event.set()
            if server_used:
                server_socket.shutdown(socket.SHUT_RDWR)
            server_socket.close()

    def get_requests(self):
        """ Get requests
        Returns:
            A list of str contains keys from clients
        """
        return self.waitting_for.keys()

    def offer_data(self, key, data):
        """ Offer data w.r.t certain key
        Args:
            key: the key of the original request
            data: respond to the request in bytes
        """
        # save prepared data to the dict
        self.waitting_for[key] = data
        # set the data prepared event to notify waiting threads
        self.data_prepared_event.set()
        self.data_prepared_event = threading.Event()

    def __tcp_link(self, sock):
        """ A thread created for each request
        It will wait until the data is prepared and send the data back
        """
        recv = sock.recv(128) # receive key in bytes
        if not recv is None and not self.stopped:
            key = bytes.decode(recv) # convert bytes to str
            self.waitting_for[key] = None
            while True:
                self.data_prepared_event.wait()
                if not self.waitting_for[key] is None:
                    sock.send(self.waitting_for[key]) # send data back
                    del self.waitting_for[key]
                    break
        sock.close()
