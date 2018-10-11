import serial


class MCU():
    def __init__(self, port, upper_limit=255, lower_limit=40, deadzone=0.02):
        self.left_power = 0
        self.right_power = 0
        self.ser = serial.Serial(port, 115200)
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.deadzone = deadzone
        if not self.ser.isOpen():
            self.ser.open()

    def stop(self):
        self.set_motors(0, 0)
        self.ser.close()

    def refresh(self):
        self.ser.write((str(self.left_power) + " " +
                        str(self.right_power)).encode())

    def __check_range(self, power):
        power_abs = abs(power)
        power_abs = 1 if power_abs > 1 else power_abs
        power_sign = 1 if power > 0 else -1

        if power_abs < self.deadzone:
            return 0
        else:
            return power_sign * int(power_abs * (self.upper_limit - self.lower_limit) + self.lower_limit)

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
