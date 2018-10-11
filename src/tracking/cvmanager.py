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

    def stop(self):
        self.stopped = True

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

            frame = imutils.resize(frame, width=self.camera_resolution)

            # get the name of item required by server
            server_required_name, server_required_index = None, None
            if self.server_enabled:
                required_key = server.get_request()
                if not required_key is None:
                    splited_key = required_key.split(',')
                    if len(splited_key) == 2:
                        server_required_name = splited_key[0]
                        server_required_index = int(splited_key[1])

            for name in self.tracking_cores:
                if not self.tracking_cores_enabled[name]:
                    continue

                (x, y, size, frames) = self.tracking_cores[name].find(frame.copy())
                self.tracking_cores_result[name] = (x, y, size)

                # encode and send frame to client
                if name == server_required_name\
                        and not server_required_index is None\
                        and len(frames) > server_required_index:
                    img_encode = cv2.imencode(
                        '.jpg', frames[server_required_index])[1]
                    data_encode = np.array(img_encode)
                    str_encode = data_encode.tostring(np.uint8)
                    server.offer_data(str_encode)

                # show frames in desktop is enabled
                if self.enable_imshow:
                    for i, f in enumerate(frames):
                        cv2.imshow(name + ": " + str(i), f)

            cv2.waitKey(1)

        self.stopped = True
        vs.stop()
        if self.server_enabled:
            server.stop()
