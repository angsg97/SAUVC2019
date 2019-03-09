import time
import math
import argparse
from tracking import CVManager
from tracking import GateTrackerV3
from tracking import Flare
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
    ap.add_argument("-o", "--output")
    ap.add_argument("-s", "--speed")
    ap.add_argument("-t", "--time") # time to turn after passing
    ap.add_argument("-ft", "--forceturn") # time to force turn after launching, 30
    ap.add_argument("-a", "--angle")
    ap.add_argument("-d", "--depth") # 80
    args = vars(ap.parse_args())

    set_speed = float(args.get('speed', 0))
    set_depth = float(args.get('depth', 0))
    time_after_passing = float(args.get('time', 0))
    time_force_turn = float(args.get('forceturn', 0))
    angle_to_turn = float(args.get('angle', 0))

    # inits CV
    cv = CVManager(0,                  # choose the first web camera as the source
                   enable_imshow=True,  # enable image show windows
                   server_port=3333,    # start stream server at port 3333
                   delay=5,
                   outputfolder=args.get("output"))
    cv.add_core("GateTracker", GateTrackerV3(), False)
    cv.add_core("Flare", Flare(), False)

    # inits MCU
    mcu = MCU(2222)

    # inits IMU
    imu = IMU("/dev/ttyUSB_IMU")

    # start subprocess
    cv.start()
    imu.start()
    mcu.start()

    imu.reset_yaw2(-angle_to_turn, 2) # for state 3

    mcu.wait()

    cv.enable_core("GateTracker")

    pidR = pidRoll(1, 0.2, 0) # 5, 0.1 , 5
    pidP = pidPitch(0.6, 0, 0)# 5 ,0.1 ,8
    pidD = pidDepth(1, 0, 0)
    pidY = pidYaw(1, 0.3, 0)
    motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0

    try:
        motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0
        counter = 0
        last_cv_gate = 0
        yaw = 0
        speed = 0
        state = 0
        timer_for_state0 = time.time()
        timer_for_state1 = 0
        timer_for_state2 = 0
        # 0 -> go find the gate
        # 1 -> continue after passing the gate
        # 2 -> find flare
        # 3 -> surfacing
        while True:
            counter += 1
            if state == 0:
                gate, _, gate_size = cv.get_result("GateTracker")
                depth = mcu.get_depth()
                pitch = imu.get_pitch()
                roll = imu.get_roll()
                speed = set_speed

                if gate is None: # just go straight
                    yaw = imu.get_yaw2(0) # original heading
                else:
                    if gate != last_cv_gate:
                        imu.reset_yaw2(-gate * 0.1, 1)
                        last_cv_gate = gate
                    else:
                        yaw = imu.get_yaw2(1) # heading with CV

                    if gate_size > 350:
                        state = 1
                if time.time() - timer_for_state0 > time_force_turn:
                    state = 1
                print('Gate', gate)
                print('GateSize', gate_size)
            # go straight
            elif state == 1:
                if timer_for_state1 == 0: # first time
                    cv.disable_core('GateTracker')
                    timer_for_state1 = time.time()
                elif time.time() - timer_for_state1 > time_after_passing:
                    state = 2
                    cv.enable_core('Flare')
                depth = mcu.get_depth()
                pitch = imu.get_pitch()
                roll = imu.get_roll()
                yaw = imu.get_yaw2(0) # original heading
                speed = set_speed
            # go to the flare
            elif state == 2:
                gate, _, gate_size = cv.get_result("Flare")
                depth = mcu.get_depth()
                pitch = imu.get_pitch()
                roll = imu.get_roll()
                speed = set_speed
                print(gate, gate_size)

                if gate is None: # just go straight
                    yaw = imu.get_yaw2(2) + 15 * math.sin(time.time())
                else:
                    if gate != last_cv_gate:
                        imu.reset_yaw2(-gate * 0.1, 1)
                        last_cv_gate = gate
                    else:
                        yaw = imu.get_yaw2(1)

                if not gate_size is None:
                    if gate_size > 200:
                        timer_for_state2 = time.time()
                if timer_for_state2 != 0 and time.time() - timer_for_state2 > 10:
                    state = 3
            # surfacing
            else:
                depth = 500
                pitch = imu.get_pitch()
                roll = imu.get_roll()
                yaw = 0
                speed = 0

            pidR.getSetValues(roll)
            pidP.getSetValues(pitch)
            pidD.getSetValues(set_depth-depth)
            pidY.getSetValues(-yaw)
            finalPidValues = add_list(pidR.start(), pidP.start(), pidD.start(), pidY.start())

            sentValues  = []
            for values in finalPidValues:
                subValues = values
                sentValues.append(subValues)

            motor_fl = sentValues[0]
            motor_fr = sentValues[1]
            motor_bl = sentValues[2] + speed
            motor_br = sentValues[3] + speed
            motor_t = sentValues[4]

            mcu.set_motors(motor_fl, motor_fr, motor_bl, motor_br, motor_t)

            if counter % 20 == 0:
                print('State:', state)
                print('Depth:', depth)
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
