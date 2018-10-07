import time
from imutils.video import VideoStream
from tracking import CVThread
from tracking import ColorDetector
from tracking import BallTracker
from mcu import MCU

def main():
    mcu = MCU(range(35, 39))
    cv = CVThread([(ColorDetector(), "ColorDetector"),
                   (BallTracker((29, 86, 6), (64, 255, 255)), "OrangeTracker")],
                  VideoStream(src=0), enable_imshow=False, server_port=3333)
    cv.start()
    try:
        while True:
            position = cv.get_result("OrangeTracker")
            print(str(position))
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
