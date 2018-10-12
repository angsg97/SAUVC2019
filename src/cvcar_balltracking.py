import time
from imutils.video import VideoStream
from tracking import CVManager
from tracking import BallTracker
from cvcar import MCU
from hardwarelib import PIDController


def main():
    mcu = MCU("/dev/ttyUSB0", 90, 40)
    cv = CVManager(VideoStream(src=0), server_port=3333)
    cv.add_core("Tracker", BallTracker((29, 86, 6), (64, 255, 255)), True)

    position = 0
    def get_position():
        return position
    def turn(power):
        mcu.set_motors(0, power)

    pid = PIDController(get_position, turn, 0.5, 0.1, 0)
    
    cv.start()
    pid.start()
    try:
        while True:
            position = cv.get_result("Tracker")
            x_error = position[0]
            print(x_error)
            if x_error is None:
                pid.pause()
            else:
                pid.resume()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        mcu.stop()
        cv.stop()


if __name__ == '__main__':
    main()
