import time
import math
import matplotlib.pyplot as plt
from collections import deque

class Plotter:
    def __init__(self):
        plt.figure(figsize=(8, 6), dpi=80)
        plt.ion()
        self.lists = {}

    def feed_data(self, name, data):
        self.lists[name] = data

    def draw(self):
        num_rows = int(len(self.lists) ** 0.5)
        num_cols = math.ceil(len(self.lists) / num_rows)

        plt.clf()
        plt.cla()
        index = 0
        for name, data in self.lists.items():
            index += 1
            y = list(data)
            x = range(len(y))
            plt.subplot(num_rows * 100 + num_cols * 10 + index)
            plt.plot(x, y)
            plt.title(name)
        plt.show()
        plt.pause(0.001)

class PID_Simulator:
    def __init__(self, name, plotter, position=0, dampling=0, weight=1):
        self.weight = weight
        self.dampling = dampling
        self.name = name
        self.plotter = plotter
        self.a = 0
        self.v = 0
        self.position = position
        self.position_history = deque(maxlen=60)
        self.last_time = time.time()

    def update(self, power):
        delta_t = 0.1

        self.a = power
        self.a -= self.v * self.dampling
        self.v += self.a * delta_t
        self.position += self.v * delta_t

        self.position_history.append(self.position)
        self.plotter.feed_data(self.name, self.position_history)

    def get_current(self):
        return self.position

def main():
    plotter = Plotter()
    cv = PID_Simulator('CV', plotter, 100, 1, 1)
    depth_sensor = PID_Simulator('Depth', plotter, 50, 3, 2)
    pitch_sensor = PID_Simulator('Pitch', plotter, 20, 1, 1)
    roll_sensor = PID_Simulator('Roll', plotter, 30, 1, 1)
    yaw_sensor = PID_Simulator('Yaw', plotter, 30, 1, 1)

    motor_fl, motor_fr, motor_bl, motor_br, motor_t = 0, 0, 0, 0, 0
    while True:
        gate = cv.get_current()
        depth = depth_sensor.get_current()
        pitch = pitch_sensor.get_current()
        roll = roll_sensor.get_current()
        yaw = yaw_sensor.get_current()

        

        cv.update(motor_bl - motor_br)
        depth_sensor.update(motor_fl + motor_fr + motor_t)
        pitch_sensor.update(motor_fl + motor_fr - motor_t)
        roll_sensor.update(motor_fl - motor_fr)
        yaw_sensor.update(motor_bl - motor_br)
        plotter.draw()

if __name__ == '__main__':
    main()
