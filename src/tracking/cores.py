""" this module contains definition of ITrackingCore interface and sample implement"""
from abc import ABCMeta, abstractclassmethod
import cv2


class ITrackingCore(metaclass=ABCMeta):
    """ The interface for all tracking cores so that CVManager can manage them"""
    @abstractclassmethod
    def find(cls, frame):
        """ Find an object in the frame

        Args:
            frame: an openCV frame in BGR

        Returns:
            (x, y, size, frames)
                the location of the object relative to center(in pixel) and frames for debug
        """


class ColorDetector(ITrackingCore):
    """ this core shows the color in the centre of the frame
    It only returns debug frame
    """

    def find(self, frame):
        height, width, _ = frame.shape
        mid_x, mid_y = width//2, height//2

        frame = cv2.GaussianBlur(frame, (15, 15), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        cv2.circle(frame, (mid_x, mid_y), 15, (0, 0, 255), 1) # draw a circle in the middle
        # show texts of both BGR and HSV value besides the circle
        cv2.putText(frame, "BGR: " + str(frame[mid_y][mid_x]) + " HSV: " + str(hsv[mid_y][mid_x]),
                    (mid_x - 100, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1, cv2.LINE_AA)
        return (None, None, None, [frame]) # no obeject to track, so always return None

class Blank(ITrackingCore):
    """ this core does nothing """
    def find(self, frame):
        return (None, None, None, [frame])

class AllChannels(ITrackingCore):
    def find(self, frame):
        # Splite channels
        b, g, r = cv2.split(frame)
        yCrCb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        y, Cr, Cb = cv2.split(yCrCb)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        return (None, None, None, [b, g, r, y, Cr, Cb, h, s, v])

class BallTracker(ITrackingCore):
    """ track object in certain color range """

    def __init__(self, color_hsv_lower, color_hsv_upper):
        self.color_lower = color_hsv_lower
        self.color_upper = color_hsv_upper

    def find(self, frame):
        _, width, _ = frame.shape
        # convert it to the HSV
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # construct a mask for the color
        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        #cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        cnts = cnts[1]
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 20:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                # show coordinate on the frame 
                cv2.putText(frame, str([int(x), int(y), int(radius)]),
                            center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                # show color of the ball on the frame 
                cv2.putText(frame, str(hsv[int(y)][int(x)]),
                            (int(x), int(y + 50)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                return (x - width//2, y - width//2, radius, [mask, frame])

        return (None, None, None, [mask, frame]) # in case a ball can not be found
