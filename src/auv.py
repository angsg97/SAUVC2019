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
    ap.add_argument("-v", "--video",
                    help="path to the (optional) video file")
    ap.add_argument("-c", "--camera",
                    help="index of camera")
    ap.add_argument("-o", "--output",
                    help="path to save the video")
    args = vars(ap.parse_args())
    if args.get("video", False):
        vs = args.get("video", False)
    elif args.get("camera", False):
        vs = int(args.get("camera", False))
    else:
        vs = 0

    # inits CV
    cv = CVManager(vs,                  # choose the first web camera as the source
                   enable_imshow=True,  # enable image show windows
                   server_port=3333,    # start stream server at port 3333
                   delay=5,
                   outputfolder=args.get("output"))
    cv.add_core("GateTracker", GateTrackerV3(), True)

    # inits MCU
    mcu = MCU(2222)

    # inits IMU
    imu = IMU("/dev/ttyUSB_IMU")

    # start subprocess
    cv.start()
    mcu.start()
    imu.start()

    pidR = pidRoll(5, 0.1, 5) # 5, 0.1 , 5
    pidP = pidPitch(5, 0.1, 8)# 5 ,0.1 ,8
    pidD = pidDepth(5, 0.1, 5)
    pidY = pidYaw(5, 0.1, 5)
    motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0

    try:
        motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0
        while True:
            gate = cv.get_result("GateTracker")[0]
            depth = mcu.get_depth()
            pinger = mcu.get_angle()
            pitch = imu.get_pitch()
            roll = imu.get_roll()
            yaw = imu.get_yaw()

            pidR = pidRoll(0,0,0)
            pidP = pidPitch(0,0,0)
            pidD = pidDepth(0,0,0)
            pidY = pidYaw(0,0,0)

            pidR.getSetValues(roll)
            pidP.getSetValues(pitch)
            pidD.getSetValues(depth)
            pidY.getSetValues(gate)
            finalPidValues = add_list(pidR.start(), pidP.start(), pidD.start(), pidY.start())

            sentValues  = []
            for values in finalPidValues:
                subValues = values / 4
                sentValues.append(subValues)

            motor_fl = sentValues[0]
            motor_fr = sentValues[1]
            motor_bl = sentValues[2]
            motor_br = sentValues[3]
            motor_t = sentValues[4]

            # Put control codes here

            mcu.set_motors(motor_fl, motor_fr, motor_bl, motor_br, motor_t)

            print('Gate:', gate)
            print('Depth:', depth)
            print('Pinger:', pinger)
            print('Pitch:', pitch)
            print('Roll:', roll)
            print('Yaw:', yaw)
            print('Motors:', (motor_fl, motor_fr, motor_bl, motor_br, motor_t))
            print()
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        cv.stop()
        imu.stop()
        mcu.stop()

if __name__ == '__main__':
    main()
