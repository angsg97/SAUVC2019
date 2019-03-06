""" Template for openCV cores test
please copy this file and feel free to modify the copy to test your own tracking core
(!!!do not add your own test file to git unless needed)
"""
import time
import argparse
import cv2
from tracking import CVManager
from tracking import ITrackingCore

class DepthCore(ITrackingCore):
    def find(self, frame):
        b, g, r = cv2.split(frame)
        blurred = cv2.GaussianBlur(b, (41, 41), 0)

        col = cv2.resize(b, (1, 1), 0)
        return col[0][0], None, None, []
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
                    help="path to the (optional) video file")
    ap.add_argument("-c", "--camera",
                    help="index of camera")
    ap.add_argument("-o","--output",
                    help="path to save the video")
    args = vars(ap.parse_args())
    if args.get("video", False):
        vs = args.get("video", False)
    elif args.get("camera", False):
        vs = int(args.get("camera", False))
    else:
        vs = 0

    cv = CVManager(vs,                  # choose the first web camera as the source
                   enable_imshow=True,  # enable image show windows
                   server_port=3333,    # start stream server at port 3333
                   delay=10,
                   outputfolder=args.get("output"))
    cv.add_core("Depth", DepthCore(), True)
    # cv.add_core("GateTrackerV2", GateTrackerV2(), True)
    cv.start()
    try:
        while True:
            print(cv.get_result("Depth"))
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        cv.stop()

if __name__ == '__main__':
    main()
