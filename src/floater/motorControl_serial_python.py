import serial
import time
arduino = serial.Serial("COM9", 9600, timeout =1 )

while True:
    print(" enter l=left , r= right, s=straight , x = stop, b= reverse")
    arduino.write(raw_input().encode())
    arduino.flush()
