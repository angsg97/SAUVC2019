import time
import argparse
from tracking import CVManager
from tracking import Flare

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
                   delay=5,
                   outputfolder=args.get("output"))
    cv.add_core("Flare", Flare(), True)
    cv.start()
    try:
        while True:
            time.sleep(0.1)
            print(cv.get_result('Flare'))
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        cv.stop()

if __name__ == '__main__':
    main()