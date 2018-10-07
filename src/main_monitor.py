import time
import numpy as np
import argparse
import cv2
import network

def decode_bytes(bytes_array):
    nparr = np.fromstring(bytes_array, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--address",
                    help="address of server")
    ap.add_argument("-p", "--port", type=int,
                    help="port of server")
    ap.add_argument("-c", "--channel",
                    help="channels to be monitored, divided by /")
    ap.add_argument("-d", "--delay", type=float, default=0.01,
                    help="refresh delay")
    args = vars(ap.parse_args())
    client = network.Client(args["address"], args["port"])
    channel_list = args["channel"].split("/")
    while True:
        for c in channel_list:
            cv2.imshow(c, decode_bytes(client.get_data(c)))
        cv2.waitKey(1)
        time.sleep(args["delay"])

if __name__ == '__main__':
    main()
