'''
a thread that constantly read from Xbee and save data to some variables then send current motor speeds to Xbee
other functions (set_depth and get_angle)just returns those variables and update motor speeds.
'''
import time
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

        self.converted = 0
        self.device = XBeeDevice(port, 9600)

        self.stopped = False

    def run(self):
        '''
        keeps sending motor values to Xbee
        '''
        self.device.open()
        while not self.stopped:
            try:
                self.depth = device.read_data(0).data.decode()
                # print("[R] DEPTH: {}".format(depth))
            except:
                # print("Something is wrong")
                pass

            motor_data = [self.m_front_left, self.m_front_right,
                          self.m_back_left, self.m_back_right, self.m_tail]
            converted_values = [self.convert(x) for x in motor_data]

            for value in converted_values:
                self.device.send_data_broadcast(bytes([value]))
        self.device.close()

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
        max_send, min_send = -1, 1
        diff_send = max_send - min_send
        max_data, min_data = 255, 0
        diff_data = max_data - min_data

        converted = self.check_range((data - min_data)/diff_data * diff_send + min_send)
        return converted


def test():
    mcu = MCU("/dev/ttyUSB0")
    mcu.start()
    start_time = time.time()
    while time.time() - start_time < 5:
        power = (time.time() - start_time) / 5 - 0.5
        mcu.set_motors(power, power, power, power, power)
        print("Depth:", mcu.get_depth())
    mcu.stop()


if __name__ == '__main__':
    test()
