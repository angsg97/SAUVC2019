import serial
import threading
import time

class IMU(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.ser = serial.Serial(port, 115200)
        if not self.ser.isOpen():
            self.ser.open()
        self.angles = (0, 0, 0)
        self.a = (0, 0, 0)
        self.w = (0, 0, 0)
        self.temperature = 36.53
        self.__package_interpreters = {0x51: self.__save_a, 0x52: self.__save_w, 0x53: self.__save_angles}
        self.__package = []
    
    def get_angles(self):
        return self.angles

    def get_acceleration(self):
        return self.a
    
    def get_angular_velocity(self):
        return self.w

    def get_temperature(self):
        return self.temperature

    def is_open(self):
        return self.ser.isOpen()

    def run(self):
        self.stopped = False
        while self.is_open() and not self.stopped:
            data = self.ser.read()[0]
            if data == 0x55:
                self.__mpu6050_decode(self.__package)
                self.__package = []
            self.__package.append(data)

        if not self.stopped:
            self.stop()
    
    def stop(self):
        self.stopped = True
        self.ser.close()

    def __save_general(self, raw_items, coefficient):
        x = raw_items[0]/32768*coefficient
        y = raw_items[1]/32768*coefficient
        z = raw_items[2]/32768*coefficient
        self.temperature = raw_items[3]/340+36.53
        return (x, y, z)

    def __save_a(self, raw_items):
        self.a = self.__save_general(raw_items, 16*9.81)
    
    def __save_angles(self, raw_items):
        self.angles = self.__save_general(raw_items, 180)
    
    def __save_w(self, raw_items):
        self.w = self.__save_general(raw_items, 180)
    
    def __bin_to_signed(self, num, size):
        return (num & ((1 << (size - 1)) - 1)) - (num & (1 << (size - 1)))

    def __check_package(self, package):
        if len(package) != 11:
            return False
        if package[0] != 0x55:
            return False
        if not package[1] in self.__package_interpreters.keys():
            return False
        sum = 0
        for i in range(10):
            sum += package[i]
        sum &= 0b11111111
        if sum != package[10]:
            return False
        return True

    def __mpu6050_decode(self, package):
        if not self.__check_package(package):
            return
        items = []
        for i in range(4):
            data = package[2 + 2*i + 1] << 8 | package[2 + 2*i]
            items.append(self.__bin_to_signed(data, 16))
        self.__package_interpreters[package[1]](items)

def main():
    """ Function for testing and demo """
    imu = IMU('/dev/ttyUSB0')
    imu.start()
    while imu.is_open():
        angles = imu.get_angles()
        a = imu.get_acceleration()
        w = imu.get_angular_velocity()
        temp = imu.get_temperature()
        print(str(angles) + '\n' + str(a) + '\n' + str(w) + '\n' + str(temp))
        time.sleep(1)

if __name__ == '__main__':
    main()
