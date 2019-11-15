from imu import IMU
import time

imu = IMU("/dev/ttyUSB0")
integration1_result = 0
integration2_result = 0

def get_depth():

    #fast integration
    last_time = time.time()
    acceleration = imu.get_accz()
    acc_diff_time = time.time() -last_time
    integration1 = acceleration*acc_diff_time
    global integration1_result += integration1
    last_time = time.time()
    #2nd integration

    vel_diff_time = acc_diff_time
    integration2 = integration1_result *acc_diff_time
    global integration2_result += integration2

    depth = integration2_result

    return depth

while True:
    print("Depth:" +str( get_depth()))





