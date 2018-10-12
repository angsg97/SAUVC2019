import time
from imutils.video import VideoStream
from tracking import CVManager
from tracking import BallTracker
from cvcar import MCU
from hardwarelib import PIDController


def main():
    mcu = MCU("com3")
    cv = CVManager(VideoStream(src=0), server_port=3333)
    cv.add_core("Tracker", BallTracker((29, 86, 6), (64, 255, 255)), True)
    cv.start()
    try:
        while True:
            position = cv.get_result("Tracker")
            x_error = position[0]
            print(x_error)
            if not x_error is None:
                mcu.set_motors(0, position[0] * 0.5)
            else:
                mcu.set_motors(0, 0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        mcu.stop()
        cv.stop()


if __name__ == '__main__':
    main()
