import sys
import select
import termios
import tty
import threading
import time
from cvcar import MCU


class KeyListener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.key = 0
        self.time_stamp = 0
        self.stopped = True

    def __get_key(self):
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.setting)
        return key

    def get_key(self):
        return (self.key, self.time_stamp)

    def run(self):
        self.stopped = False
        self.setting = termios.tcgetattr(sys.stdin)
        try:
            while True:
                self.key = self.__get_key()
                if self.key == '\x03':
                    self.stopped = True
                    break
                self.time_stamp = time.time()
        except Exception:
            pass
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.setting)


def main():
    mcu = MCU("/dev/ttyUSB0", 100, 40)
    key_listener = KeyListener()
    key_listener.start()
    while not key_listener.stopped:
        key, t = key_listener.get_key()
        if time.time() - t > 0.05:
            mcu.set_motors(0, 0)

        elif key == 'w':
            mcu.set_motors(1, 0)
        elif key == 'q':
            mcu.set_motors(1, -1)
        elif key == 'e':
            mcu.set_motors(1, 1)

        elif key == 's':
            mcu.set_motors(-1, 0)
        elif key == 'a':
            mcu.set_motors(0, -1)
        elif key == 'd':
            mcu.set_motors(0, 1)

        elif key == 'x':
            mcu.set_motors(-1, 0)
        elif key == 'z':
            mcu.set_motors(-1, -1)
        elif key == 'c':
            mcu.set_motors(-1, 1)
        time.sleep(0.04)


if __name__ == "__main__":
    main()
