import time
from imutils.video import VideoStream
from tracking import CVManager
from tracking import BallTracker
from cvcar import MCU
from hardwarelib import PIDController
from hardwarelib import ParabolaPredictor


def main():
    mcu = MCU("/dev/ttyUSB0", 120, 40, 0.03)
    cv = CVManager(VideoStream(src=0), server_port=3333)
    cv.add_core("Tracker", BallTracker((30, 40, 60), (50, 200, 255)), True)
    start_time = time.time() 

    x_predict = ParabolaPredictor()
    x_predict.put_data(0, 0)

    x_error_last = 0
    x_error = [0]
    x_output = [0]
    def get_x_position():
        val = x_predict.predict(time.time()- start_time)\
        # print(str(time.time()-start_time) + "\t" + str(val) + "\t", end='')
        return val
    def turn(power):
        # print(str(x_error[0]) + "\t" + str(power))
        x_output[0] = power
        mcu.set_motors(y_output[0], power)
    pid_x = PIDController(get_x_position, turn, 0.001, 0.002, 0.000, 1000, True, minimal_delay_ms=25)

    y_predict = ParabolaPredictor()
    y_predict.put_data(0, 0)

    y_error = [0]
    y_output = [0]
    def get_y_position():
        val = y_predict.predict(time.time() - start_time)
        print(str(time.time()-start_time) + "\t" + str(val) + "\t", end='')
        return val
    def forward(power):
        print(str(y_error[0] - 130) + "\t" + str(power))
        x_output[0] = power
        y_output[0] = power
        mcu.set_motors(power, 0)
    pid_y = PIDController(get_y_position, forward, 0.003, 0.002, 0, 500, True, minimal_delay_ms=30)
    
    cv.start()
    pid_x.start()
    pid_y.start()
    try:
        while True:
            cv.wait()
            position = cv.get_result("Tracker")
            x_error[0] = position[0]
            if x_error[0] is None:
                if x_error_last < 0:
                    mcu.set_motors(0, -0.6)
                elif x_error_last > 0:
                    mcu.set_motors(0, 0.6)
                else:
                    mcu.set_motors(0, 0)
                pid_x.pause()
                pid_y.pause()
            else:
                if x_error_last != x_error[0]:
                    x_predict.put_data(time.time()-start_time, x_error[0])
                    y_error[0] = 130 - position[2]
                    y_predict.put_data(time.time()-start_time, y_error[0])
                    x_error_last = x_error[0]
                pid_x.resume()
                pid_y.resume()
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping remaining threads...")
        mcu.stop()
        pid_x.stop()
        pid_y.stop()
        cv.stop()


if __name__ == '__main__':
    main()
