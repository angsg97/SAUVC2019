"""

PSEUDOCODE:
1. we need to capture the data in bytes, the IMU values are stdout data
2. Process that data return it as strings or numbers, assign it as attributes of the object
3. create a class that will organize all those data and make calling of those function much more intuitive
   class may contain

Possible reasons why the code will not run
- wrong port in the maincpp file, to check port in use,
To find out which port is being used by the IMU
1.type in terminal  "ls /dev/ > dev_list_1.txt"
this store list of device before pluggin in the port
2. Plug in IMU to a serial port
3.Then type in terminal "ls /dev/ | diff --suppress-common-lines -y - dev_list_1.txt"
4. Change the serial port connection from the maincpp file.



"""
import sys
import os
import subprocess
import threading
import time


class IMU(threading.Thread):
    # This class then inherits the threading.Thread class

    def __init__(self):
        threading.Thread.__init__(self)

        self.yaw = 0
        self.pitch = 0
        self.roll = 0

        self.angx = 0
        self.angy = 0
        self.angz = 0

        self.accx = 0
        self.accy = 0
        self.accz = 0

        self.magx = 0
        self.magy = 0
        self.magz = 0

        self.finalParse = []
        self.stopped = False

    def stop(self):
        self.stopped = True

    def run(self):
        self.proc = subprocess.Popen(os.path.join(
            sys.path[0], './imu-core'), bufsize=1024, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        # once the IMU class has been instantiated,
        # allow './SAUVC' program to run and read the values from the terminal
        while not self.stopped:
            self.output_parser("Acceleration:")
            self.accx, self.accy, self.accz = self.get_converted_parse()
            self.output_parser("Angular Rate:")
            self.angx, self.angy, self.angz = self.get_converted_parse()
            self.output_parser("YawPitchRoll:")
            self.yaw, self.pitch, self.roll = self.get_converted_parse()
            self.output_parser("Magnetic:")
            self.magx, self.magy, self.magz = self.get_converted_parse()
        self.proc.kill()

    def get_converted_parse(self):
        return float(self.finalParse[0]), float(self.finalParse[1]), float(self.finalParse[2])

    def output_parser(self, datatype):
        for i in range(5):
            storebytes = self.proc.stdout.readline()
            output = storebytes.decode()
            # Everytime data is needed, we need the latest reading from the IMU
            # we then decode this values as they are in bytes as it is read from the terminal
            # print(self.output)
            if datatype in output:
                output_1 = output.replace(datatype, "", 1)
                output_2 = output_1.replace('(', "", 1)
                output_3 = output_2.replace(")", ";", 1)
                self.finalParse = output_3.split(";")
                return

        self.finalParse = (-1, -1, -1)

    def get_yaw(self):
        return self.yaw

    def get_pitch(self):
        return self.pitch

    def get_roll(self):
        return self.roll

    def get_angx(self):
        return self.angx

    def get_angy(self):
        return self.angy

    def get_angz(self):
        return self.angz

    def get_accx(self):
        return self.accx

    def get_accy(self):
        return self.accy

    def get_accz(self):
        return self.accz

    def get_magx(self):
        return self.magx

    def get_magy(self):
        return self.magy

    def get_magz(self):
        return self.magz


# Test code
if __name__ == '__main__':
    def test():
        try:
            imu = IMU()
            imu.start()
            while True:
                print("yaw = ", imu.get_yaw())
                print("pitch = ", imu.get_pitch())
                print("roll = ", imu.get_roll())

                print("angx = ", imu.get_angx())
                print("angy = ", imu.get_angy())
                print("angz = ", imu.get_angz())

                print("accx = ", imu.get_accx())
                print("accy = ", imu.get_accy())
                print("accz = ", imu.get_accz())

                print("magx = ", imu.get_magx())
                print("magy = ", imu.get_magy())
                print("magz = ", imu.get_magz())

                print()
                time.sleep(1)
        except KeyboardInterrupt:
            imu.stop()
    test()
