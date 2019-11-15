from network import Server

'''
a thread that constantly read from Xbee and save data to some variables then send current motor speeds to Xbee
other functions (set_depth and get_angle)just returns those variables and update motor speeds.
'''
import time
import traceback
from collections import deque
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
        self.depth_queue = deque(maxlen=10)
        self.last_depth = 0
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
                self.connected = True
                if len(nums) == 2:
                    self.connected = True
                    self.depth_queue.append(int(nums[0]))
                    self.angle = int(nums[1])
                response = "{},{},{},{},{}\n".format(
                    self.convert(-self.m_front_left),
                    self.convert(-self.m_front_right),
                    self.convert(-self.m_back_left),
                    self.convert(-self.m_back_right),
                    self.convert(self.m_tail))
                response = response.encode('utf-8')
                server.offer_data(r, response)
                break
        server.stop()

    def stop(self):
        self.stopped = True
    
    def check_range_float(self, value, limit):
        if value > limit:
            return limit
        if value < -limit:
            return -limit
        return value

    def set_motors(self, m_front_left, m_front_right, m_back_left, m_back_right, m_tail):
        self.m_front_left = self.check_range_float(m_front_left, 0.5)
        self.m_front_right = self.check_range_float(m_front_right, 0.5)
        self.m_back_left = self.check_range_float(m_back_left, 1)
        self.m_back_right = self.check_range_float(m_back_right, 1)
        self.m_tail = self.check_range_float(m_tail, 0.5)

    def get_angle(self):
        return self.angle

    def get_depth(self):
        if len(self.depth_queue) == 0:
            return 0
        return sum(self.depth_queue) / len(self.depth_queue)

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

    def wait(self):
        print('waiting for MCU connection....')
        while not self.connected:
            time.sleep(0.1)
        print('MCU connected')


def test():
    pass


if __name__ == '__main__':
    test()
