""" Contains the CVManager class """
import os
import platform
import threading
import numpy as np
import imutils
from imutils.video import VideoStream
import cv2
import network
from tracking.cores import ITrackingCore


class CVManager(threading.Thread):
    """ Class to manage openCV activities

    It shares frame from one camera among multiple cores (see ITrackingCore)
    and provides a universal way to manage these cores, access their result and debug
    """

    def __init__(self, video_stream, camera_resolution=640, enable_imshow=False, server_port=None, delay=1):
        """ Inits the CVManager
        (use start method to launch it)
        Args:
            video_stream: VideoStream created by imutils
            camera_resolution: expected width of the frame, if it is not a None value,
                the manager will resize the original video stream
            enable_imshow: show images in GUI windows (can not be True at CLI only environment,
                see monitor.py for more information about CLI debug)
            server_port: port number for stream service (see monitor.py)
                set to None to disable the stream service
        """
        # inits threading.Thread
        threading.Thread.__init__(self)
        # save arguments and inits class variables
        self.tracking_cores = {}
        self.tracking_cores_enabled = {}
        self.tracking_cores_result = {}
        # load video stream
        if isinstance(video_stream, int):
            self.video_stream = VideoStream(src=video_stream)
        elif isinstance(video_stream, str):
            self.video_stream = cv2.VideoCapture(video_stream)
        elif isinstance(video_stream, (imutils.video.videostream.VideoStream, cv2.VideoCapture)):
            self.video_stream = video_stream
        self.camera_resolution = camera_resolution
        self.enable_imshow = enable_imshow and CVManager.__check_display()
        self.server_enabled = not server_port is None
        self.server_port = server_port
        self.stopped = True
        self.new_frame_event = threading.Event()
        self.delay = delay

    def add_core(self, name, core: ITrackingCore, enabled=False):
        """ Add a core to the manager
        Args:
            name: the name of the added core which is used for management and result access
            core: an Instance of ITrackingCore
            enabled: enable the core immediately
                (the core can also be enabled by enable_core method)
        """
        self.tracking_cores[name] = core
        self.tracking_cores_enabled[name] = enabled
        self.tracking_cores_result[name] = (None, None, None)

    def enable_core(self, name):
        """ Enable an existent core
        Ars:
            name: name of the core
        """
        self.tracking_cores_enabled[name] = True

    def disable_core(self, name):
        """ Disable an existent core
        Ars:
            name: name of the core
        """
        self.tracking_cores_enabled[name] = False

    def get_result(self, name):
        """ Get certain core's last result
        Ars:
            name: name of the core
        """
        return self.tracking_cores_result[name]

    def wait(self):
        """ Wait for the next frame to be proceeded """
        self.new_frame_event.wait()

    def stop(self):
        """ Stop the Cv manager """
        self.stopped = True
        if self.server:
            self.server.stop()

    @staticmethod
    def __encode(frame):
        """ Encode a frame to bytes """
        img_encode = cv2.imencode('.jpg', frame)[1] # code the frame to jpg saved in a buffer
        data_encode = np.array(img_encode) # convert the buffer to numpy array
        # convert numpy array to bytes which required by Server class
        return data_encode.tostring(np.uint8)

    @staticmethod
    def __check_display():
        """ Check if there is a display available """
        sysstr = platform.system()
        if sysstr =="Windows":
            return True # Assume windows always have displays
        else:
            return 'DISPLAY' in os.environ

    def run(self):
        """ Main body for cv manager
        (It should only be called by threading.Thread, use start() to launch it)
        """
        self.stopped = False
        vs = self.video_stream.start() \
            if isinstance(self.video_stream, imutils.video.videostream.VideoStream) \
            else self.video_stream
        # Inits video streaming server
        if self.server_enabled:
            self.server = network.Server(self.server_port)
            self.server.start()
        while not self.stopped:
            frame = vs.read() \
                if isinstance(self.video_stream, imutils.video.videostream.VideoStream) \
                else vs.read()[1]

            if frame is None:
                if isinstance(self.video_stream, imutils.video.videostream.VideoStream):
                    print("Something went wrong when trying to start video stream :(")
                    break
                else:
                    # Reset cap to replay it if it is a video
                    vs.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

            # Resize frame if required
            if not self.camera_resolution is None:
                frame = imutils.resize(frame, width=self.camera_resolution)

            # get a list of the names of items required by server
            server_requests = self.server.get_requests() if self.server_enabled else []

            # run each core
            for name in self.tracking_cores:
                if not self.tracking_cores_enabled[name]: # bypass disabled core
                    continue

                (x, y, size, frames) = self.tracking_cores[name].find(frame.copy()) # run core
                self.tracking_cores_result[name] = (x, y, size) # save result

                for i, f in enumerate(frames):
                    frame_name = name + "," + str(i)
                    # encode and send frame to client
                    if frame_name in server_requests:
                        self.server.offer_data(frame_name, CVManager.__encode(f))
                    # show frames in desktop is enabled
                    if self.enable_imshow:
                        cv2.imshow(frame_name, f)

            self.new_frame_event.set() # set the event so wait() method can be released
            self.new_frame_event = threading.Event()
            cv2.waitKey(self.delay) # wait

        # stop the manager
        if isinstance(self.video_stream, imutils.video.videostream.VideoStream):
            vs.stop()
        self.stop()
