""" Template for openCV cores test
please copy this file and feel free to modify the copy to test your own tracking core
(!!!do not add your own test file to git unless needed)
"""
import time
from imutils.video import VideoStream
from tracking import CVManager
from tracking import ColorDetector
from tracking import BallTracker


def main():
    """ Entry of the program """
    cv = CVManager([(ColorDetector(), "ColorDetector"),
                    (BallTracker((8, 180, 110), (19, 255, 160)), "OrangeTracker")],
                   VideoStream(src=0),
                   enable_imshow=False,
                   server_port=3333)
    cv.start()
    try:
        while True:
            print(str(cv.get_result("OrangeTracker")))
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        cv.stop()


if __name__ == '__main__':
    main()
