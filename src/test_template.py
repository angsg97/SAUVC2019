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
    cv = CVManager(VideoStream(src=0),  # choose the first web camera as the source
                   enable_imshow=True,  # enable image show windows
                   server_port=3333)    # start stream server at port 3333
    cv.add_core("ColorDetector", ColorDetector(), True) # add a color detector core and enable it
    cv.add_core("OrangeTracker", BallTracker((8, 180, 110), (19, 255, 160)), True)
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
