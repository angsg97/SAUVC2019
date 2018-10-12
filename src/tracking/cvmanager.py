import threading
import numpy as np
import imutils
import cv2
import network
from tracking.cores import ITrackingCore


class CVManager(threading.Thread):
    """ Thread to manange openCV activities"""

    def __init__(self, video_stream, camera_resolution=640, enable_imshow=False, server_port=None):
        threading.Thread.__init__(self)
        self.tracking_cores = {}
        self.tracking_cores_enabled = {}
        self.tracking_cores_result = {}
        self.video_stream = video_stream
        self.camera_resolution = camera_resolution
        self.enable_imshow = enable_imshow
        self.server_enabled = not server_port is None
        self.server_port = server_port
        self.stopped = True
        self.new_frame_event = threading.Event()

    def add_core(self, name, core: ITrackingCore, enabled=False):
        self.tracking_cores[name] = core
        self.tracking_cores_enabled[name] = enabled
        self.tracking_cores_result[name] = (None, None, None)

    def enable_core(self, name):
        self.tracking_cores_enabled[name] = True

    def disable_core(self, name):
        self.tracking_cores_enabled[name] = False

    def get_result(self, name):
        return self.tracking_cores_result[name]

    def wait(self):
        self.new_frame_event.wait()

    def stop(self):
        self.stopped = True

    @staticmethod
    def encode(frame):
        img_encode = cv2.imencode('.jpg', frame)[1]
        data_encode = np.array(img_encode)
        return data_encode.tostring(np.uint8)

    def run(self):
        self.stopped = False
        vs = self.video_stream.start()
        if self.server_enabled:
            server = network.Server(3333)
            server.start()
        while not self.stopped:
            frame = vs.read()

            if frame is None:
                print("Something went wrong when trying to start video stream :(")
                break
            
            if not self.camera_resolution is None:
                frame = imutils.resize(frame, width=self.camera_resolution)

            # get the names of items required by server
            server_requests = server.get_requests() if self.server_enabled else []

            for name in self.tracking_cores:
                if not self.tracking_cores_enabled[name]:
                    continue

                (x, y, size, frames) = self.tracking_cores[name].find(frame.copy())
                self.tracking_cores_result[name] = (x, y, size)

                for i, f in enumerate(frames):
                    frame_name = name + "," + str(i)
                    # encode and send frame to client
                    if frame_name in server_requests:
                        server.offer_data(frame_name, CVManager.encode(f))
                    # show frames in desktop is enabled
                    if self.enable_imshow:
                        cv2.imshow(frame_name, f)

            self.new_frame_event.set()
            self.new_frame_event = threading.Event()
            cv2.waitKey(1)

        self.stopped = True
        vs.stop()
        if self.server_enabled:
            server.stop()
