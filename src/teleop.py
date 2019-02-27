"""" This program allows users to use keyboard to control the cv car
and steam back the camera image at port 3333 (use monitor.py to watch)
"""
import sys
import select
import termios # only on Linux
import tty
import threading
import time
from imutils.video import VideoStream
from tracking import CVManager
from tracking import Blank
from mcu import MCU

KEY_MAP = {
    't': (1, 0, 0, 0, 0),
    'g': (-1, 0, 0, 0, 0),
    'y': (0, 1, 0, 0, 0),
    'h': (0, -1, 0, 0, 0),
    'u': (0, 0, 1, 0, 0),
    'j': (0, 0, -1, 0, 0),
    'i': (0, 0, 0, 1, 0),
    'k': (0, 0, 0, -1, 0),
    'o': (0, 0, 0, 0, 1),
    'l': (0, 0, 0, 0, -1),
    ' ': (0, 0, 0, 0, 0)
}

class KeyListener(threading.Thread):
    """ Listens all keyboard events """
    def __init__(self):
        threading.Thread.__init__(self)
        self.key = 0
        self.time_stamp = 0
        self.stopped = True

    def __get_key(self):
        # redirect stdin to read the last keyboared event
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1) # read key
        # restore stdin setting
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.setting)
        return key

    def get_key(self):
        return (self.key, self.time_stamp)

    def run(self):
        self.stopped = False
        self.setting = termios.tcgetattr(sys.stdin) # save original stdin setting
        try:
            while True:
                self.key = self.__get_key() # wait for next key (like getch)
                if self.key == '\x03': # in case ctrl-c is pressed
                    self.stopped = True # exit the program
                    break
                self.time_stamp = time.time()
        except Exception:
            pass
        finally:
            # restore stdin setting
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.setting)


def main():
    """ main body """
    mcu = MCU("/dev/ttyUSB0")
    key_listener = KeyListener()
    key_listener.start()
    # prepare video streaming
    cv = CVManager(VideoStream(src=0), server_port=3333)
    cv.add_core("Stream", Blank(), True)
    cv.start()
    overall_speed = 0.4
    while not key_listener.stopped:
        key, t = key_listener.get_key()

        # if the key is released more than 0.05s
        # stop the car
        if time.time() - t > 0.05:
            mcu.set_motors(0, 0, 0, 0, 0)
        else:
            if key == 'm':
                overall_speed += 0.01
                print("Speed: ", overall_speed)
            if key == 'n':
                overall_speed -= 0.01
                print("Speed: ", overall_speed)

            # map keyboared to mcu actions
            action = KEY_MAP.setdefault(key, (0, 0, 0, 0, 0))
            action = [i * overall_speed for i in action] # reduce speed
            print(action)
            mcu.set_motors(action[0], action[1], action[2], action[3], action[4])

        time.sleep(0.04)
    cv.stop()

if __name__ == "__main__":
    main()
