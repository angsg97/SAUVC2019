import serial
import threading
import time

class IMU(threading.Thread):
    def __init__(self, port):
        """ Create a new IMU reader 
        Args:
            port: port to JY-61 IMU, usually looks loke /dev/ttyUSBx on Linux
        """
        threading.Thread.__init__(self)
        self.ser = serial.Serial(port, 115200)
        if not self.ser.isOpen(): # the serial may already started
            self.ser.open()
        self.angles = (0, 0, 0)
        self.a = (0, 0, 0)
        self.w = (0, 0, 0)
        self.temperature = 36.53
        # the map of process methods corresponding to package types
        self.__package_interpreters = {0x51: self.__save_a, 0x52: self.__save_w, 0x53: self.__save_angles}
        self.stopped = True
    
    def get_angles(self):
        """ Get angles
        Returns:
            (poll(x), pitch(y), yaw(z)) in degree
        """
        return self.angles

    def get_acceleration(self):
        """ Get acceleration
        
        Returns:
            (a_x, a_y, a_z) in m^2/s
        """
        return self.a
    
    def get_angular_velocity(self):
        """ Get angular velocity
        Returns:
            (w_x, w_y, w_z) in degree/s
        """
        return self.w

    def get_temperature(self):
        """ Get temperature measured by module
        Returns:
            a float number which is the temperature in ℃
        """
        return self.temperature

    def is_open(self):
        """ check if the serial port is opened 
        Note that it is opened when creating the instance
        """
        return self.ser.isOpen()

    def is_running(self):
        """ check if the thread is running """
        return not self.stopped

    def run(self):
        """ The main body for the reader thread
        You should not call this method directly
        Use start to start a new thread so it can run parallel
        """
        self.stopped = False
        package = []
        while self.is_open() and not self.stopped:
            data = self.ser.read()[0]
            # TODO may loose frame when there is 0x55 in package body
            if data == 0x55: # 0x55 indicates the head of a new package
                self.__mpu6050_decode(package) # so decode the old one
                package = [] # and empty the buffer
            package.append(data)

        if not self.stopped: # if it was not stopped by user
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
        """ convert from unsigned bin to signed integer with corresponding size """
        return (num & ((1 << (size - 1)) - 1)) - (num & (1 << (size - 1)))

    def __check_package(self, package):
        """ Check if the package is correct """
        if len(package) != 11: # check length
            return False
        if package[0] != 0x55: # check the head of the package
            return False
        # check the package type
        if not package[1] in self.__package_interpreters.keys():
            return False
        # check sum
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
            # combine the higher bits with the lower bits
            data = package[2 + 2*i + 1] << 8 | package[2 + 2*i]
            # then converted it to a signed bumber
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
