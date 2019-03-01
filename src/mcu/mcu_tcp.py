from network import Server

'''
a thread that constantly read from Xbee and save data to some variables then send current motor speeds to Xbee
other functions (set_depth and get_angle)just returns those variables and update motor speeds.
'''
import time
import traceback
from threading import Thread
from digi.xbee.devices import XBeeDevice


class MCU(Thread):
    def __init__(self, port):
        Thread.__init__(self)

        self.m_front_left = 0
        self.m_front_right = 0
        self.m_back_left = 0
        self.m_back_right = 0
        self.m_tail = 0
        self.depth = 0
        self.angle = 0
        self.port = port
        self.stopped = False
        self.connected = False

    def run(self):
        server = Server(self.port)
        server.start()
        while not self.stopped:
            requests = server.get_requests()
            for r in requests:
                nums = r.split(',')
                if len(nums) == 2:
                    self.connected = True
                    self.depth = int(nums[0])
                    self.angle = int(nums[1])
                # self.depth = 
                response = "{},{},{},{},{}\n".format(
                    self.convert(self.m_front_left),
                    self.convert(self.m_front_right),
                    self.convert(self.m_back_left),
                    self.convert(self.m_back_right),
                    self.convert(self.m_tail))
                response = response.encode('utf-8')
                server.offer_data(r, response)
                break
        server.stop()

    def stop(self):
        self.stopped = True

    def set_motors(self, m_front_left, m_front_right, m_back_left, m_back_right, m_tail):
        self.m_front_left = m_front_left
        self.m_front_right = m_front_right
        self.m_back_left = m_back_left
        self.m_back_right = m_back_right
        self.m_tail = m_tail

    def get_angle(self):
        return self.angle

    def get_depth(self):
        return self.depth

    def check_range(self, data):
        data = int(data)
        if data > 255:
            return 255
        if data < 0:
            return 0
        return data

    def convert(self, data):
        """
        Converts data from range -1 - 1 to 0 - 255
        Returns converted value
        """
        max_send, min_send = 255, 0
        diff_send = max_send - min_send
        max_data, min_data = 1, -1
        diff_data = max_data - min_data

        converted = self.check_range(
            (data - min_data)/diff_data * diff_send + min_send)
        return converted


def test():
    pass


if __name__ == '__main__':
    test()