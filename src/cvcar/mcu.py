import RPi.GPIO as GPIO


class MCU():
    def __init__(self, pinnum, init_rate=100):
        self.rate = init_rate
        self.velocity = 10
        GPIO.setmode(GPIO.BOARD)

        pwm = {}
        for i, pin in enumerate(pinnum):
            GPIO.setup(pin, GPIO.OUT)
            pwm[i] = GPIO.PWM(pin, init_rate)
            pwm[i].start(0)
        self.pwml1, self.pwml2, self.pwmr1, self.pwmr2 = pwm[0], pwm[1], pwm[2], pwm[3]

    def turn_left(self):
        self.pwml1.ChangeDutyCycle(self.velocity)
        self.pwml2.ChangeDutyCycle(0)
        self.pwmr1.ChangeDutyCycle(0)
        self.pwmr2.ChangeDutyCycle(0)

    def turn_right(self):
        self.pwmr1.ChangeDutyCycle(self.velocity)
        self.pwmr2.ChangeDutyCycle(0)
        self.pwml1.ChangeDutyCycle(0)
        self.pwml2.ChangeDutyCycle(0)

    def forward(self):
        self.pwmr1.ChangeDutyCycle(self.velocity)
        self.pwml1.ChangeDutyCycle(self.velocity)
        self.pwmr2.ChangeDutyCycle(0)
        self.pwml2.ChangeDutyCycle(0)

    def backward(self):
        self.pwmr2.ChangeDutyCycle(self.velocity)
        self.pwml2.ChangeDutyCycle(self.velocity)
        self.pwmr1.ChangeDutyCycle(0)
        self.pwml1.ChangeDutyCycle(0)

    def accelerate(self):
        self.velocity += 10

    def deaccelerate(self):
        self.velocity -= 10
