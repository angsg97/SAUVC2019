import time
import argparse
from tracking import CVManager
from tracking import GateTrackerV3
from mcu import MCU
from imu import IMU

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
    mcu = MCU("/dev/ttyUSB0")

    # inits IMU
    imu = IMU()

    # start subprocess
    cv.start()
    mcu.start()
    imu.start()
    try:
        motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0
        while True:
            gate = cv.get_result("GateTracker")[0]
            depth = mcu.get_depth()
            pinger = mcu.get_angle()
            pitch = imu.get_pitch()
            roll = imu.get_roll()
            yaw = imu.get_yaw()

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
