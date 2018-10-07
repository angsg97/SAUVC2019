import time
from imutils.video import VideoStream
from tracking import *
from mcu import MCU

def main():
    mcu = MCU(range(35, 39))
    cv = CVThread([(BallTracker((29, 86, 6), (64, 255, 255)), "OrangeTracker")],
                  VideoStream(src=0), enable_imshow=False, server_port=3333)
    cv.start()
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

if __name__ == '__main__':
    main()
