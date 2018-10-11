import serial


class MCU():
    def __init__(self, port):
        self.left_power = 0
        self.right_power = 0
        self.ser = serial.Serial(port, 115200)
        if not self.ser.isOpen():
            self.ser.open()

    def stop(self):
        self.set_motors(0, 0)
        self.ser.close()

    def refresh(self):
        self.ser.write((str(self.left_power) + " " +
                        str(self.right_power)).encode())

    def __check_range(self, power):
        power = int(power)
        return 255 if power > 255 else -255 if power < -255 else power

    def set_left_motor(self, power):
        self.left_power = self.__check_range(power)
        self.refresh()

    def set_right_motor(self, power):
        self.right_power = self.__check_range(power)
        self.refresh()

    def set_motors(self, power_forward, power_turn_L):
        self.left_power = self.__check_range(power_forward + power_turn_L)
        self.right_power = self.__check_range(power_forward - power_turn_L)
        self.refresh()
