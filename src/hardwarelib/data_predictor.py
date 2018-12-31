""" This module does data prediction """
from collections import deque


class ParabolaPredictor():
    """ Use quadratic function to predict future value w.r.t time
    It will find a quadratic function that fits the last three value
    and use that function to predict value of the system at certain time
    """
    def __init__(self, n=2):
        """ Inits the parabola predictor
        Args:
            n: the maximum order of the predictor (should always <= 2)
                when n = 1, it is a linear predictor
                when n = 2, it is a parabola predictor
        """
        self.past_value = deque(maxlen=(n + 1))

    def put_data(self, time, data):
        """ Provides data to the predictor
        Args:
            time: x value of the data point
            data: y value of the data point
        """
        point = (time, data)
        for t, _ in self.past_value: # prevent same data point
            if time == t:
                return
        self.past_value.append(point)

    def predict(self, time):
        """ predict the value at certain time """
        # return last value for 0 order case
        if len(self.past_value) == 1:
            return self.past_value[-1][1]
        # return the prediction result of the linear function
        elif len(self.past_value) == 2:
            k = (self.past_value[-2][1]-self.past_value[-1][1])\
                / (self.past_value[-2][0]-self.past_value[-1][0])
            return k*(time-self.past_value[-1][0]) + self.past_value[-1][1]
        # return the prediction of quadratic function
        else:
            x1 = self.past_value[-3][0]
            y1 = self.past_value[-3][1]
            x2 = self.past_value[-2][0]
            y2 = self.past_value[-2][1]
            x3 = self.past_value[-1][0]
            y3 = self.past_value[-1][1]
            a = -(-x2*y1+x3*y1+x1*y2-x3*y2-x1*y3+x2*y3) / \
                ((-x1+x2)*(x2-x3)*(-x1+x3))
            b = -(x2*x2*y1-x3*x3*y1-x1*x1*y2+x3*x3*y2+x1 *
                  x1*y3-x2*x2*y3) / ((x1-x2)*(x1-x3)*(x2-x3))
            c = -(-x2*x2*x3*y1+x2*x3*x3*y1+x1*x1*x3*y2-x1*x3*x3*y2 -
                  x1*x1*x2*y3+x1*x2*x2*y3) / ((x1-x2)*(x1-x3)*(x2-x3))
            return time*time*a+time*b+c

# module test
if __name__ == "__main__":
    predictor = ParabolaPredictor()
    predictor.put_data(1, 9)
    x = predictor.predict(4)
    if x == 9:
        print(True)
    else:
        print("error")

    predictor.put_data(2, 25)
    y = predictor.predict(3)
    if y == 41:
        print(True)
    else:
        print("error")

    predictor.put_data(3, 49)
    z = predictor.predict(4)
    if z == 81:
        print(True)
    else:
        print("error")

    predictor.put_data(4,90)
    z=predictor.predict(5)
    print(z)
    predictor.put_data(4,90)
    zx=predictor.predict(6)
