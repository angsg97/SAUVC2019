"""" This program allows users to use keyboard to control the cv car
and steam back the camera image at port 3333 (use monitor.py to watch)
"""
import time
from mcu import MCU

def main():
    """ main body """
    mcu = MCU(2222)
    mcu.start()
    power = 0
    step = 0.1

    print('watting for connection....')
    while not mcu.connected:
        time.sleep(0.1)

    while True:
        print('Depth:', mcu.get_depth())
        print('Angle:', mcu.get_angle())
        power += step
        if abs(power) > 0.5:
            step = -step
        mcu.set_motors(power, power, power, power, power)
        print('Power:', power)
        print()
        time.sleep(0.5)
    mcu.stop()

if __name__ == "__main__":
    main()
