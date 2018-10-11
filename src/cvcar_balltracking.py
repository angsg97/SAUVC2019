import time
from imutils.video import VideoStream
from tracking import CVManager
from tracking import BallTracker
from cvcar import MCU


def main():
    mcu = MCU(range(35, 39))
    cv = CVManager(VideoStream(src=0), server_port=3333)
    cv.add_core("Tracker", BallTracker((29, 86, 6), (64, 255, 255)), True)
    cv.start()
    try:
        while True:
            position = cv.get_result("Tracker")
            print(str(position))
            if position[0] is None:
                mcu.turn_right()  # turn to search object
            else:
                if position[0] < -50:
                    mcu.turn_right()
                elif position[0] > 50:
                    mcu.turn_left()
                else:
                    mcu.forward()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        cv.stop()


if __name__ == '__main__':
    main()
