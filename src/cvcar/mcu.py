""" Interfaces with the CV car's MCU module """
import time
import serial


class MCU():
    """ Interfaces with the CV car's MCU module to control motors """
    def __init__(self, port: str, upper_limit=255, lower_limit=40, deadzone=0.02):
        """
        Args:
            port: name of the serial port the MCU connected to
                (Usually a path in Linux like "/dev/ttyUSB0")
            upper_limit: (optional) maximum power,
                default value is 255 which is the physical maximum power
            lower_limit: (optional) minimum power,
                refer to __linear_mapping for more information
            deadzone: (optional) deadzone, for input power smaller than deadzone,
                the MCU will output 0 directly
        """
        self.left_power = 0
        self.right_power = 0
        self.ser = serial.Serial(port, 115200) # initialize serial
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.deadzone = deadzone
        self.stopped = False
        if not self.ser.isOpen():
            self.ser.open()

    def stop(self):
        """ Stops serial and all motors """
        self.set_motors(0, 0)
        self.stopped = True
        time.sleep(0.1) # wait for mcu to actually stop
        self.ser.close() # then stop serial

    def refresh(self):
        """ Sends current powers to mcu """
        self.ser.write((str(self.left_power) + " " +
                        str(self.right_power)).encode())

    def __check_range(self, power):
        """ limits power to [-1, 1] """
        if power < -1:
            return -1
        elif power > 1:
            return 1
        return power

    def __linear_mapping(self, power, check_range=True):
        """ linearly maps power from [-1, 1] to [-maxPower, maxPower]
            also implement deadzone, range check and minimal power

            The algorithm will be:
            [-1, -deadzone]         ->  [-maxPower, -minPower]
            [-deadzone, deadzone]   ->  0
            [deadzone, 1]           ->  [minPower, maxPower]
            This is for better control of motors
        """
        if self.stopped:
            return 0
        # check range and get the absolute value
        power_abs = self.__check_range(abs(power)) if check_range else abs(power)
        power_sign = 1 if power > 0 else -1 # get sign of original power

        # check deadzone
        if power_abs < self.deadzone:
            return 0

        # do the mapping
        return power_sign * \
            int(power_abs * (self.upper_limit - self.lower_limit) + self.lower_limit)

    def set_left_motor(self, power):
        """ Sets power of left motor

        Args:
            power: a float value in [-1, 1]
        """
        self.left_power = self.__linear_mapping(power)
        self.refresh()

    def set_right_motor(self, power):
        """ Sets power of right motor

        Args:
            power: a float value in [-1, 1]
        """
        self.right_power = self.__linear_mapping(power)
        self.refresh()

    def set_motors(self, power_forward, power_turn_L):
        """ Sets all motors of the car

        Args:
            power_forward: the power for forwarding in [-1, 1]
            power_turn_L: the power for turing left,
                        (-1 means turn right at maximum speed and 1 means turn left)
        """
        power_forward = self.__check_range(power_forward)
        power_turn_L = self.__check_range(power_turn_L)
        self.left_power = self.__linear_mapping(power_forward + power_turn_L)
        self.right_power = self.__linear_mapping(power_forward - power_turn_L)
        self.refresh()
