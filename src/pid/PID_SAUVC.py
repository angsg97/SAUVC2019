import time


class pid():

    def __init__(self, Kp=2, Ki=0, Kd=0):
        # getValues will be the sensor values that you have. extracted from other classes
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setPoint = 0
        self.getValues = 0
        # initializes the time values we need to create  the loop
        self.sampleTime = 2/100
        # we need to set this as a fixed interval, at 0 PID will  update every time possible.
        # time.time() returns a floating point number in seconds
        # It might be a good idea to set this at a faster rate due to the lag time of data transfer between the xbees
        self.currentTime = time.time()
        self.lastTime = self.currentTime
        self.last_error = 0.0
        self.output = 0
        self.Pterm = 0.0
        self.Iterm = 0.0
        self.Dterm = 0.0
        self.windup_guard = 10.0

    def clear(self):
        # we can call this value to reset the P I D terms, this makes our code more modular
        self.Pterm = 0.0
        self.Iterm = 0.0
        self.Dterm = 0.0
        self.last_error = 0.0
        # Windup Guard
        # initialise constraints to limit values of kp, ki and kd, to prevent values from getting too large
        self.windup_guard = 10.0
        self.output = 0.0

    def update(self):
        setPoint = self.setPoint
        self.feedback = self.getValues

        error = setPoint - self.feedback
        self.currentTime = time.time()
        delta_time = self.currentTime - self.lastTime
        delta_error = error - self.last_error
        # update pid code after sample_time defined elapsed
        if delta_time >= self.sampleTime:
            self.Pterm = self.Kp * error
            self.Iterm += error * delta_time
            if self.Iterm < -self.windup_guard:
                self.Iterm = -self.windup_guard
            elif self.Iterm > self.windup_guard:
                self.Iterm = self.windup_guard
            self.Dterm = 0.0
            if delta_time > 0:
                self.Dterm = delta_error / delta_time
            # Remember last time and last error for next calculation
            self.lastTime = self.currentTime
            self.last_error = error
            self.output = self.Pterm + \
                (self.Ki * self.Iterm) + (self.Kd * self.Dterm)

    def getSetValues(self, getValues):
        self.getValues = getValues
        return self.getValues

    def setKp(self, proportional_gain):
        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        """Determines how aggressively the PID reacts to the current error with setting Integral Gain"""
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
        self.Kd = derivative_gain

    def setWindup(self, windup):
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral terms accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        self.windup_guard = windup

    def setSampleTime(self, sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.sample_time = sample_time


class pidRoll(pid):
    def start(self):
        self.update()
        return self.rollMotorValues()

    def rollMotorValues(self):
        if self.output <= 100 and self.output >= -100:
            motorBottomLeft = self.output/100
            motorBottomRight = self.output/(-100)
            # take note that when error is positive, the roll is anti_clockwise
            # Thus, we make motorBottomLeft push forward
            # and the motorBottomRight to push in reverse.
            # here we assume that the max pidOutput is 100
            return(motorBottomLeft, motorBottomRight, 0, 0, 0)
        elif self.output > 100:
            motorBottomLeft = 1
            motorBottomRight = -1
            return (motorBottomLeft, motorBottomRight, 0, 0, 0)
        elif self.output < -100:
            motorBottomLeft = -1
            motorBottomRight = 1
            return (motorBottomLeft, motorBottomRight, 0, 0, 0)


class pidPitch(pid):
    def start(self):
        self.update()
        return self.pitchMotorValues()

    def pitchMotorValues(self):
        if self.output <= 100 and self.output >= -100:
            motorBottomLeft = self.output/(100)
            motorBottomRight = self.output/(100)
            motorTail = self.output/(-100)
            return (motorBottomLeft, motorBottomRight, 0, 0, motorTail)
        elif self.output > 100:
            motorBottomLeft = 1
            motorBottomRight = 1
            motorTail = -1
            return (motorBottomLeft, motorBottomRight, 0, 0, motorTail)
        elif self.output < -100:
            motorBottomLeft = -1
            motorBottomRight = -1
            motorTail = 1
            return (motorBottomLeft, motorBottomRight, 0, 0, motorTail)


class pidDepth(pid):
    def start(self):
        self.update()
        return self.depthMotorValues()

    def depthMotorValues(self):
            # currently, output value is assumed to be less than 100, but that will have to be mapped properly depending on the output values
        if self.output <= 100 and self.output >= -100:
            self.speed = self.output/100
        elif self.output > 100:
            self.speed = 1
        elif self.output < -100:
            self.speed = -1
        motorBottomLeft = self.speed
        motorBottomRight = self.speed
        motorTail = self.speed
        return (motorBottomLeft, motorBottomRight, 0, 0, motorTail)


class pidYaw(pid):
    def start(self):
        self.update()
        return self.YawMotorValues()

    def YawMotorValues(self):
        if self.output <= 100 and self.output >= - 100:
            self.speed = self.output / 100
        elif self.output > 100:
            self.speed = 1
        elif self.output < 100:
            self.speed = -1

        motorForwardRight = self.speed
        motorForwardLeft = -self.speed
        return [0, 0, motorForwardLeft, motorForwardRight, 0]


def test():
    pidR = pidRoll()
    pidD = pidDepth()
    pidP = pidPitch()
    pidY = pidYaw()

    pidR.getSetValues(0)
    pidD.getSetValues(0)
    pidP.getSetValues(0)
    pidY.getSetValues(0)

    pidD.start()
    pidR.start()
    pidP.start()
    pidY.start()

if __name__ == "__main__":
    test()