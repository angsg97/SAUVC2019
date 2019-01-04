import time
from imutils.video import VideoStream
from tracking import CVManager
from tracking import BallTracker
from cvcar import MCU
from hardwarelib import PIDController
from hardwarelib import ParabolaPredictor


def main():
    # inits MCU
    mcu = MCU("/dev/ttyUSB0", 120, 40, 0.03)
    # inits CV Manager
    cv = CVManager(VideoStream(src=0, resolution=(320, 240)), server_port=3333)
    cv.add_core("Tracker", BallTracker((30, 40, 60), (50, 200, 255)), True)

    # inits PID controller in X axis (turn left / right)
    x_output = [0] # set it as list so that inner function can access it
    # callback function for PID controller which returns current error in x axis
    def get_x_position():
        cv.wait()
        return cv.get_result("Tracker")[0]
    # callback function to set motors
    def turn(power):
        x_output[0] = power
        mcu.set_motors(y_output[0], x_output[0])
    # inits PID controller
    pid_x = PIDController(get_x_position, turn, 0.001, 0.002, 0, 1000, True, minimal_delay_ms=50)

    # inits PID controller in Y axis (foraward / backward)
    y_output = [0]
    def get_y_position():
        cv.wait()
        return 130 - cv.get_result("Tracker")[2]
    def forward(power):
        y_output[0] = power
        mcu.set_motors(y_output[0], x_output[0])
    pid_y = PIDController(get_y_position, forward, 0.003, 0.002, 0, 500, True, minimal_delay_ms=50)

    # Starts everything
    cv.start()
    pid_x.start()
    pid_y.start()
    try:
        x_error_last = 0
        while True:
            cv.wait()
            position = cv.get_result("Tracker")
            # if can not find object
            # stop PID and turn to last known direction
            if position[0] is None:
                if x_error_last < 0:
                    mcu.set_motors(0, -0.6)
                elif x_error_last > 0:
                    mcu.set_motors(0, 0.6)
                else:
                    mcu.set_motors(0, 0)
                pid_x.pause()
                pid_y.pause()
            # or resume PID and save last x position
            else:
                x_error_last = position[0]
                pid_x.resume()
                pid_y.resume()
    # catch KeyboardInterrupt (caused by Ctrl-C)
    except KeyboardInterrupt:
        pass
    # so we can properly stop the program
    finally:
        print("Stopping remaining threads...")
        mcu.stop()
        pid_x.stop()
        pid_y.stop()
        cv.stop()


if __name__ == '__main__':
    main()
