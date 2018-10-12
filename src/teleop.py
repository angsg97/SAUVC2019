import sys
import select
import termios
import tty
from cvcar import MCU


def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, SETTING)
    return key


def main():
    mcu = MCU("/dev/ttyUSB0", 90, 40)
    while True:
        key = getKey()
        if key == '\x03':
            mcu.stop()
            break
        elif key == 'a':
            mcu.set_motors(0, -0.5)
        elif key == 's':
            mcu.set_motors(0, 0)
        elif key == 'd':
            mcu.set_motors(0, 0.5)


if __name__ == "__main__":
    SETTING = termios.tcgetattr(sys.stdin)
    try:
        main()
    except Exception:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, SETTING)
