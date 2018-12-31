""" A tool that receives streaming from CV Manager and show them in GUI

Usuage:
    python monitor.py -a address -p port -c ChannelName1,index/ChannelName2,index/...
    example: python monitor.py -a 127.0.0.1 -p 3333 -c OrangeTracker,1  #this receives streaming video from test_template 
"""
import time
import argparse
import numpy as np
import cv2
import network

def decode_bytes(bytes_array):
    nparr = np.fromstring(bytes_array, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def main():
    # get CLI arguments
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

    # initialize client
    client = network.Client(args["address"], args["port"])
    # get channels list
    channel_list = args["channel"].split("/")
    while True:
        for c in channel_list:
            # send channel name to server and show received frames
            cv2.imshow(c, decode_bytes(client.get_data(c)))
        cv2.waitKey(1)
        time.sleep(args["delay"])

if __name__ == '__main__':
    main()
