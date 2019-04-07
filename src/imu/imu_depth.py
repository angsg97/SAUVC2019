from imu import IMU
import time

imu = IMU()

def get_depth():
    last_time =time.time()
    acceleration = imu.get_accy()

    acc_current_time = time.time()
    acc_diff_time = acc_current_time -last_time
    integration1 = acceleration*acc_diff_time
    integration1_result += integration1

    last_time = current_time

    vel_current_time= time.time()
    vel_diff_time = vel_current_time - last_time
    integration2 = integration1_result *vel_diff_time
    integration2_result += integration2

    depth = integration2_result

    return depth



while True:
    print("Depth:" + get_depth())









        #for 2nd integration


