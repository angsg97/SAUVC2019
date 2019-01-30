""" Template for openCV cores test
please copy this file and feel free to modify the copy to test your own tracking core
(!!!do not add your own test file to git unless needed)
"""
import time
import argparse
from tracking import CVManager
from tracking import GateTrackerV2

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
                    help="path to the (optional) video file")
    ap.add_argument("-c", "--camera",
                    help="index of camera")
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
                   delay=5)
    cv.add_core("GateTracker", GateTrackerV2(), True)
    cv.start()
    try:
        while True:
            print(cv.get_result("GateTracker"))
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        cv.stop()

if __name__ == '__main__':
    main()
