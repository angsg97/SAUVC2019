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
    ap.add_argument("-s", "--speed")
    args = vars(ap.parse_args())

    if args.get("video", False):
        vs = args.get("video", False)
    elif args.get("camera", False):
        vs = int(args.get("camera", False))
    else:
        vs = 0
    
    set_speed = args.get('speed', 0)
    if set_speed is None:
        set_speed = 0
    set_speed = float(set_speed)
    speed = 0

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
    imu.start()
    mcu.start()

    time.sleep(2)
    imu.delta_yaw = imu.get_yaw()
    print('Target yaw: ', imu.delta_yaw)
    mcu.wait()

    pidR = pidRoll(1, 0, 0) # 5, 0.1 , 5
    pidP = pidPitch(0.6, 0, 0)# 5 ,0.1 ,8
    pidD = pidDepth(1, 0, 0)
    pidY = pidYaw(1, 0.1, 0)
    motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0

    try:
        motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0
        counter = 0
        last_cv_gate = 0
        gate_passed = False
        while True:
            counter += 1
            gate, _, gate_size = cv.get_result("GateTracker")
            depth = mcu.get_depth()
            pinger = mcu.get_angle()
            pitch = imu.get_pitch()
            roll = imu.get_roll()

            if gate_passed or gate is None: # just go straight
                yaw = imu.get_yaw2(0)
                speed = set_speed
            else:
                if gate != last_cv_gate:
                    imu.reset_yaw2(-gate * 0.2, 1)
                    last_cv_gate = gate
                else:
                    yaw = imu.get_yaw2(1)

                if gate_size > 350:
                    gate_passed = True

            pidR.getSetValues(roll)
            pidP.getSetValues(pitch)
            pidD.getSetValues(70-depth)
            pidY.getSetValues(-yaw)
            finalPidValues = add_list(pidR.start(), pidP.start(), pidD.start(), pidY.start())

            sentValues  = []
            for values in finalPidValues:
                subValues = values
                sentValues.append(subValues)

            motor_fl = sentValues[0]
            motor_fr = sentValues[1]
            motor_bl = sentValues[2] + set_speed
            motor_br = sentValues[3] + set_speed
            motor_t = sentValues[4]

            # Put control codes here

            mcu.set_motors(motor_fl, motor_fr, motor_bl, motor_br, motor_t)

            if counter % 5 == 0:
                print('Gate', gate)
                print('GateSize', gate_size)
                print('Passed?', gate_passed)
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
        cv.stop()
        imu.stop()
        mcu.stop()

if __name__ == '__main__':
    main()
