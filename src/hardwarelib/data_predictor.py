from collections import deque


class ParabolaPredictor():
    # please do not set a value that is more than 3
    def __init__(self,n=3): 
        self.past_value = deque(maxlen=n)

    def put_data(self, time, data):
        piont = (time, data)
        for t,v in self.past_value:
            if time==t:
                return
            else:
                pass
        self.past_value.append(piont)
        print(self.past_value)

    def predict(self, time):
        if len(self.past_value) == 1:
            return self.past_value[-1][1]
        elif len(self.past_value) == 2:
            k = (self.past_value[-2][1]-self.past_value[-1][1])\
                / (self.past_value[-2][0]-self.past_value[-1][0])
            return k*(time-self.past_value[-1][0]) + self.past_value[-1][1]
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


if __name__ == "__main__":
    a = ParabolaPredictor()
    a.put_data(1, 9)
    x = a.predict(4)
    if x == 9:
        print(True)
    else:
        print("error")

    a.put_data(2, 25)
    y = a.predict(3)
    if y == 41:
        print(True)
    else:
        print("error")

    a.put_data(3, 49)
    z = a.predict(4)
    if z == 81:
        print(True)
    else:
        print("error")

    a.put_data(4,90)
    z=a.predict(5)
    print(z)
    a.put_data(4,90)
    zx=a.predict(6)

