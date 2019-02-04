import math
import cv2
import numpy as np
from tracking import ITrackingCore


class TwoPointLine:
    def __init__(self, cv_line):
        self.x1, self.y1, self.x2, self.y2 = cv_line

    def reverse(self):
        self.x1, self.y1, self.x2, self.y2 = self.x2, self.y2, self.x1, self.y1


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_line(line):
        return Vector((line.x2 - line.x1), (line.y2 - line.y1))

    def dot(self, other_vec):
        return self.x * other_vec.x + self.y * other_vec.y

    def norm(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def angle(self, other_vec):
        if abs(self.dot(other_vec)/(self.norm()*other_vec.norm())) > 1:
            return 0
        return math.acos(self.dot(other_vec)/(self.norm()*other_vec.norm())) * 180 / math.pi

    def add_vector(self, other_vec):
        return Vector((self.x + other_vec.x), (self.y + other_vec.y))


class GateTrackerV2(ITrackingCore):

    def __possible_line(self, line):
        minimal_dy = 70
        maximal_dx = 20
        if abs(line.x2 - line.x1) < maximal_dx and abs(line.y2 - line.y1) > minimal_dy:
            return True
        return False

    def __possible_gate(self, line1, line2):
        # make sure two lines are from button(1) to top(2)
        if line1.y2 < line1.y1:
            line1.reverse()
        if line2.y2 < line2.y1:
            line2.reverse()
        # if two lines cross, can not be gate
        if (line1.x1 - line2.x1) * (line1.x2 - line2.x2) < 0:
            return False
        # find the left one and the right one
        line_L, line_R = (
            line1, line2) if line1.x1 < line2.x1 else (line2, line1)
        # find the top and button one, from left(1) to right(2)
        line_U = TwoPointLine(
            (line_L.x2, line_L.y2, line_R.x2, line_R.y2))
        line_D = TwoPointLine(
            (line_L.x1, line_L.y1, line_R.x1, line_R.y1))

        # convert to vector
        vec_L = Vector.from_line(line_L)
        vec_R = Vector.from_line(line_R)
        vec_U = Vector.from_line(line_U)
        vec_D = Vector.from_line(line_D)
        if vec_U.norm() == 0 or vec_D.norm() == 0:
            return False

        # check parallel
        if vec_L.angle(vec_R) > 10:
            return False

        if not (70 < vec_L.angle(vec_U) < 110 and 70 < vec_R.angle(vec_U) < 100):
            return False

        if not (70 < vec_L.angle(vec_D) < 110 and 70 < vec_R.angle(vec_D) < 100):
            return False

        if not 2/3 < (vec_L.add_vector(vec_R).norm() / vec_D.add_vector(vec_U).norm()) < 1.5:
            return False

        return True

    def find(self, frame):
        # Splite channelsec
        b, g, r = cv2.split(frame)

        # Find edges
        blurred = cv2.GaussianBlur(b, (11, 31), 0)
        edges = cv2.Canny(blurred, 300, 700, apertureSize=5)
        edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))

        # find lines
        lines_frame = frame.copy()
        results_frame = frame.copy()  # np.zeros(b.shape, np.uint8)
        minLineLength = 50
        maxLineGap = 15
        lines = cv2.HoughLinesP(edges, 1, np.pi/360, 20, None,
                                minLineLength, maxLineGap)
        # if not lines is None:
        gates = []
        if not lines is None:
            for line1 in lines:
                line1 = TwoPointLine(line1[0])
                cv2.line(lines_frame, (line1.x1, line1.y1),
                         (line1.x2, line1.y2), (0, 0, 255), 3)
                if not self.__possible_line(line1):
                    continue
                for line2 in lines:
                    line2 = TwoPointLine(line2[0])
                    if not self.__possible_line(line2):
                        continue
                    if self.__possible_gate(line1, line2):
                        gates.append((line1, line2))

        def gate_total(gate):
            line1, line2 = gate
            return (abs(line1.y1 - line1.y2) +
                    abs(line2.y1 - line2.y2))
        x = None
        width = None
        if gates:
            gates.sort(key=gate_total, reverse=True)
            gate = gates[0]
            line1, line2 = gate
            x = (line1.x1 + line1.x2 + line2.x1 + line2.x2) / \
                4 - (frame.shape[1] // 2)
            width = abs((line1.x1 + line1.x2) - (line2.x1 + line2.x2)) / 2
            cv2.line(results_frame, (line1.x1, line1.y1),
                     (line1.x2, line1.y2), (0, 0, 255), 3)
            cv2.line(results_frame, (line2.x1, line2.y1),
                     (line2.x2, line2.y2), (0, 0, 255), 3)
        return (x, None, width, [blurred, edges, lines_frame, results_frame])


class GateTrackerV3(ITrackingCore):

    def __possible_line(self, line):
        minimal_dy = 70
        maximal_dx = 40
        if abs(line.x2 - line.x1) < maximal_dx and abs(line.y2 - line.y1) > minimal_dy:
            return True
        return False

    def __sub_score_core(self, x):
        return 1/(x**6 + 1)

    def __sub_score(self, value, centre, error_allowed):
        return self.__sub_score_core((value - centre) / error_allowed * 0.5)

    def __possible_gate(self, gate):
        line1, line2 = gate
        # make sure two lines are from button(1) to top(2)
        if line1.y2 < line1.y1:
            line1.reverse()
        if line2.y2 < line2.y1:
            line2.reverse()
        # if two lines cross, can not be gate
        if (line1.x1 - line2.x1) * (line1.x2 - line2.x2) < 0:
            return False
        # find the left one and the right one
        line_L, line_R = (
            line1, line2) if line1.x1 < line2.x1 else (line2, line1)
        # find the top and button one, from left(1) to right(2)
        line_U = TwoPointLine(
            (line_L.x2, line_L.y2, line_R.x2, line_R.y2))
        line_D = TwoPointLine(
            (line_L.x1, line_L.y1, line_R.x1, line_R.y1))

        # convert to vector
        vec_L = Vector.from_line(line_L)
        vec_R = Vector.from_line(line_R)
        vec_U = Vector.from_line(line_U)
        vec_D = Vector.from_line(line_D)
        if vec_U.norm() == 0 or vec_D.norm() == 0:
            return 0

        total_score = 1

        # check parallel
        total_score *= self.__sub_score(vec_L.angle(vec_R), 0, 10)
        # check perpendicular
        total_score *= self.__sub_score(vec_L.angle(vec_U), 90, 20)
        total_score *= self.__sub_score(vec_R.angle(vec_U), 90, 20)
        total_score *= self.__sub_score(vec_L.angle(vec_D), 90, 20)
        total_score *= self.__sub_score(vec_R.angle(vec_D), 90, 20)
        # check ratio
        total_score *= self.__sub_score(
            (vec_L.add_vector(vec_R).norm() / vec_D.add_vector(vec_U).norm()), 1, 0.5)
        # check vertical
        x_vec = Vector(1, 0)
        total_score *= self.__sub_score(x_vec.angle(vec_L), 90, 30)
        total_score *= self.__sub_score(x_vec.angle(vec_R), 90, 30)

        return total_score

    def find(self, frame):
        # Splite channelsec
        b, g, r = cv2.split(frame)

        # Find edges
        blurred = cv2.GaussianBlur(b, (11, 31), 0)
        edges = cv2.Canny(blurred, 300, 700, apertureSize=5)
        edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))

        # find lines
        lines_frame = frame.copy()
        results_frame = frame.copy()  # np.zeros(b.shape, np.uint8)
        minLineLength = 50
        maxLineGap = 15
        lines = cv2.HoughLinesP(edges, 1, np.pi/360, 20, None,
                                minLineLength, maxLineGap)
        # if not lines is None:
        gates = []
        if not lines is None:
            for line1 in lines:
                line1 = TwoPointLine(line1[0])
                cv2.line(lines_frame, (line1.x1, line1.y1),
                         (line1.x2, line1.y2), (0, 0, 255), 3)
                if not self.__possible_line(line1):
                    continue
                for line2 in lines:
                    line2 = TwoPointLine(line2[0])
                    if not self.__possible_line(line2):
                        continue
                    gates.append((line1, line2))

        x = None
        width = None
        if gates:
            gates.sort(key=self.__possible_gate, reverse=True)
            gate = gates[0]
            score = self.__possible_gate(gate)
            if score > 0.2:
                line1, line2 = gate
                x = (line1.x1 + line1.x2 + line2.x1 + line2.x2) / 4 - (frame.shape[1] // 2)
                width = abs((line1.x1 + line1.x2) - (line2.x1 + line2.x2)) / 2
                cv2.line(results_frame, (line1.x1, line1.y1), (line1.x2, line1.y2), (0, 255 - int(score * 255), int(score * 255)), 3)
                cv2.line(results_frame, (line2.x1, line2.y1), (line2.x2, line2.y2), (0, 255 - int(score * 255), int(score * 255)), 3)
        return (x, None, width, [blurred, edges, lines_frame, results_frame])
