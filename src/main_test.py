import time
from imutils.video import VideoStream
from tracking import *


def main():
    cv = CVThread([(ColorDetector(), "ColorDetector"),
                   (BallTracker((8, 180, 110), (19, 255, 160)), "OrangeTracker")],
                  VideoStream(src=0), enable_imshow=False, server_port=3333)
    cv.start()
    while True:
        print(str(cv.get_result("OrangeTracker")))
        time.sleep(0.1)

if __name__ == '__main__':
    main()
