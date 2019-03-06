import time
import argparse
from tracking import CVManager
from tracking import GateTrackerV3
from tracking import ITrackingCore
import cv2
from mcu import MCU
from imu import IMU
from pid import *

class EStop(ITrackingCore):
    def find(self, frame):
        b, g, r = cv2.split(frame)
        blurred = cv2.GaussianBlur(b, (41, 41), 0)
        col = cv2.resize(b, (1, 1), 0)
        return col[0][0], None, None, []

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
    ap.add_argument("-t", "--time")
    args = vars(ap.parse_args())

    if args.get("video", False):
        vs = args.get("video", False)
    elif args.get("camera", False):
        vs = int(args.get("camera", False))
    else:
        vs = 0
    
    set_speed = float(args.get('speed', 0))
    set_time = float(args.get('time', 0))

    print('Speed', set_speed)
    print('Time', set_time)

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
    cv.add_core("EStop", EStop(), True)

    # inits MCU
    mcu = MCU(2222)

    # inits IMU
    imu = IMU("/dev/ttyUSB_IMU")

    # start subprocess
    cv.start()
    imu.start()
    mcu.start()

    mcu.wait()

    start_time = time.time()
    depth_speed = 0

    pidR = pidRoll(1, 0.2, 0) # 5, 0.1 , 5
    pidP = pidPitch(0.6, 0, 0)# 5 ,0.1 ,8
    pidD = pidDepth(0, 0, 0)
    pidY = pidYaw(1, 0.3, 0)
    motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0

    try:
        motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0
        counter = 0
        last_cv_gate = 0
        gate_passed = False
        while time.time() - start_time < set_time:
            counter += 1
            gate, _, gate_size = cv.get_result("GateTracker")
            depth = mcu.get_depth()
            pinger = mcu.get_angle()
            pitch = imu.get_pitch()
            roll = imu.get_roll()

            if not cv.get_result('EStop')[0] is None:
                if cv.get_result('EStop')[0] < 20:
                    break

            if gate_passed or gate is None: # just go straight
                yaw = imu.get_yaw2(0)
            else:
                if gate != last_cv_gate:
                    imu.reset_yaw2(-gate * 0.1, 1)
                    last_cv_gate = gate
                else:
                    yaw = imu.get_yaw2(1)

                if gate_size > 350:
                    gate_passed = True

            if abs(yaw) > 10:
                speed = 0
            else:
                speed = set_speed
            
            if abs((time.time() - start_time) % 5) < 1 and time.time() - start_time > 10:
                depth_speed = 0.4
            else:
                depth_speed = 0

            pidR.getSetValues(roll)
            pidP.getSetValues(pitch)
            pidD.getSetValues(70-depth)
            pidY.getSetValues(-yaw)
            finalPidValues = add_list(pidR.start(), pidP.start(), pidD.start(), pidY.start())

            sentValues  = []
            for values in finalPidValues:
                subValues = values
                sentValues.append(subValues)

            motor_fl = sentValues[0] + depth_speed
            motor_fr = sentValues[1] + depth_speed
            motor_bl = sentValues[2] + set_speed
            motor_br = sentValues[3] + set_speed
            motor_t = sentValues[4] + depth_speed

            # Put control codes here

            mcu.set_motors(motor_fl, motor_fr, motor_bl, motor_br, motor_t)

            if counter % 20 == 0:
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
        mcu.set_motors(0, 0, 0, 0, 0)
        print("Stopping remaining threads...")
        cv.stop()
        imu.stop()
        mcu.stop()

if __name__ == '__main__':
    main()
