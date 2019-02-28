"""" This program allows users to use keyboard to control the cv car
and steam back the camera image at port 3333 (use monitor.py to watch)
"""
import time
from mcu import MCU


def main():
    """ main body """
    mcu = MCU("/dev/ttyUSB0")
    mcu.start()
    while True:
        print('Depth:', mcu.get_depth())
        time.sleep(1)

if __name__ == "__main__":
    main()
