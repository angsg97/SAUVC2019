import time
import argparse
from tracking import CVManager
from tracking import GateTrackerV3
from mcu import MCU
from imu import IMU
from pid import *

def add_list(list1, list2, list3 ,list4):
    finalListValues = []
    for i in range(5):
        a = list1[i]
        b = list2[i]
        c = list3[i]
        d = list4[i]

        finalValues = a + b + c + d
        finalListValues.append(finalValues)
    return finalListValues

def main():
    # read arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--speed")
    args = vars(ap.parse_args())

    set_speed = args.get('speed', 0)
    if set_speed is None:
        set_speed = 0
    set_speed = float(set_speed)
    speed = 0

    # inits MCU
    mcu = MCU(2222)

    # inits IMU
    imu = IMU("/dev/ttyUSB_IMU")

    # start subprocess
    imu.start()
    mcu.start()

    mcu.wait()

    start_time = time.time()
    depth_speed = 0

    pidR = pidRoll(1, 0.2, 0) # 1, 0 , 0
    pidP = pidPitch(0.6, 0, 0)# 5 ,0.1 ,8
    pidD = pidDepth(0, 0, 0)
    pidY = pidYaw(1, 0.4, 0)
    motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0

    try:
        motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0
        counter = 0
        while True:
            counter += 1
            depth = mcu.get_depth()
            pinger = mcu.get_angle()
            pitch = imu.get_pitch()
            roll = imu.get_roll()
            yaw = imu.get_yaw2()

            pidR.getSetValues(roll)
            pidP.getSetValues(pitch)
            pidD.getSetValues(70-depth)
            pidY.getSetValues(-yaw)
            finalPidValues = add_list(pidR.start(), pidP.start(), pidD.start(), pidY.start())

            sentValues  = []
            for values in finalPidValues:
                subValues = values
                sentValues.append(subValues)
            
            if abs((time.time() - start_time) % 5) < 1:
                depth_speed = 0.4
            else:
                depth_speed = 0

            motor_fl = sentValues[0] + depth_speed
            motor_fr = sentValues[1] + depth_speed
            motor_bl = sentValues[2] + set_speed
            motor_br = sentValues[3] + set_speed
            motor_t = sentValues[4] + depth_speed

            mcu.set_motors(motor_fl, motor_fr, motor_bl, motor_br, motor_t)

            if counter % 5 == 0:
                print('Depth:', depth)
                print('Pinger:', pinger)
                print('Pitch:', pitch)
                print('Roll:', roll)
                print('Yaw:', imu.get_yaw2())
                print('Yaw_sent:', yaw)
                print('Motors: %.2f %.2f %.2f %.2f %.2f'%(motor_fl, motor_fr, motor_bl, motor_br, motor_t))
                print()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        imu.stop()
        mcu.stop()

if __name__ == '__main__':
    main()
