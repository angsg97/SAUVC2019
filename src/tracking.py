import threading
import time
from abc import ABCMeta, abstractclassmethod
import cv2
import imutils


class ITrackingCore(metaclass=ABCMeta):
    @abstractclassmethod
    def find(self, frame):
        """Find an object in the frame

        Args:
            frame: an openCV frame in BGR

        Return:
            (x, y, size, frames) the location of the object relative to center(in pixel) and frames for debug
        """
        pass


class ColorDetector(ITrackingCore):
    """ show the color in the middle of the frame"""

    def find(self, frame):
        height, width, _ = frame.shape
        mid_x, mid_y = width//2, height//2

        frame = cv2.GaussianBlur(frame, (15, 15), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        cv2.circle(frame, (mid_x, mid_y), 15, (0, 0, 255), 1)
        cv2.putText(frame, "BGR: " + str(frame[mid_y][mid_x]) + " HSV: " + str(hsv[mid_y][mid_x]),
                    (mid_x - 100, mid_y - 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1, cv2.LINE_AA)
        return (None, None, None, [frame])


class BallTracker(ITrackingCore):
    """ track object in certain color range """

    def __init__(self, color_hsv_lower, color_hsv_upper):
        self.color_lower = color_hsv_lower
        self.color_upper = color_hsv_upper

    def find(self, frame):
        height, width, _ = frame.shape
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
        cnts=cnts[1]
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
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                cv2.putText(frame, str([int(x), int(y), int(radius)]),
                            center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, str(hsv[int(y)][int(x)]),
                            (int(x), int(y + 50)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                return (x - width//2, y - width//2, radius, [mask, frame])

        return (None, None, None, [mask, frame])


class CVThread(threading.Thread):
    """ Thread to manange openCV activities"""

    def __init__(self, tracking_cores: [(ITrackingCore, str)],
                 video_stream, enable_imshow=False, camera_resolution=640):
        threading.Thread.__init__(self)
        self.tracking_cores = tracking_cores
        self.video_stream = video_stream
        self.enable_imshow = enable_imshow
        self.camera_resolution = camera_resolution
        self.result_dict = {}

    def get_result(self, name):
        return self.result_dict.get(name, (None, None, None))

    def run(self):
        vs = self.video_stream.start()
        while True:
            frame = vs.read()

            if frame is None:
                print("Something went wrong when trying to start video stream :(")
                break

            frame = imutils.resize(frame, width=self.camera_resolution)

            for core, name in self.tracking_cores:
                (x, y, size, frames) = core.find(frame.copy())
                # dict in python is thread safe
                self.result_dict[name] = (x, y, size)
                if self.enable_imshow:
                    for i, f in enumerate(frames):
                        cv2.imshow(name + ": " + str(i), f)

            key = cv2.waitKey(1) & 0xFF

            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break

            time.sleep(0.01)

        vs.stop()
