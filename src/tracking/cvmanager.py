import threading
import time
import numpy as np
import imutils
import cv2
import network
from tracking.cores import ITrackingCore


class CVManager(threading.Thread):
    """ Thread to manange openCV activities"""

    def __init__(self, tracking_cores: [(ITrackingCore, str)],
                 video_stream, enable_imshow=False, camera_resolution=640, server_port=None):
        threading.Thread.__init__(self)
        self.tracking_cores = tracking_cores
        self.video_stream = video_stream
        self.enable_imshow = enable_imshow
        self.camera_resolution = camera_resolution
        self.result_dict = {}
        self.server_enabled = not server_port is None
        self.server_port = server_port
        self.stopped = True

    def get_result(self, name):
        return self.result_dict.get(name, (None, None, None))

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

            for core, name in self.tracking_cores:
                (x, y, size, frames) = core.find(frame.copy())
                self.result_dict[name] = (x, y, size)

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

            key = cv2.waitKey(1) & 0xFF

            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break

            time.sleep(0.01)

        vs.stop()
        if self.server_enabled:
            server.stop()
