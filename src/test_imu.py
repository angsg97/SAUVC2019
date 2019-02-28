import time
import argparse
from imu import IMU

def main():
    # read arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port",
                    help="path for serial port")
    args = vars(ap.parse_args())

    # inits IMU
    imu = IMU(args.get("port", '/dev/ttyUSB1'))

    # start subprocess
    imu.start()

    try:
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
        pass
    finally:
        print("Stopping remaining threads...")
        imu.stop()

if __name__ == '__main__':
    main()
