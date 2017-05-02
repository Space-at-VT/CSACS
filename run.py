

from vnpy import *           # Core Library for VN-100 interfacing
import sys
import os
import time
from datetime import datetime

""" Set Up Empty Arrays for Program """

pitch_history = []
roll_history = []
yaw_history = []
pitch_rate_history = []
roll_rate_history = []
yaw_rate_history = []
current_time = []
augmented_current_time = []
i = 0

""" Connect to VectorNav VN-100 using vn.core library """

vs = VnSensor()
vs.connect("/dev/ttyUSB1", 115200)

""" Connect to Haydon-Kerk Motors and Motor Controllers """
import serial
outP = serial.Serial(port="/dev/ttyUSB0", baudrate=57600, bytesize=8,
                     parity='N', stopbits=1, timeout=2)  # Pitch Motor
out = serial.Serial(port="/dev/ttyUSB2", baudrate=57600, bytesize=8,
                    parity='N', stopbits=1, timeout=2)  # Roll Motor

# Check if connected (DEBUG ONLY)
# outP.isOpen()
# out.isOpen()


""" Graphics Options """


# Only do this if the Stop button has not been clicked
def dynamic_balance():
    pry = vs.readYawPitchRoll()
    pitch = round(pry.y, 8)
    roll = round(pry.z, 8)

    if pitch >= 10:
        movePmotor = 'I500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
    elif pitch <= -10:
        movePmotor = 'I-500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
    elif roll >= 10:
        moveRmotor = 'I500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
    elif roll <= -10:
        moveRmotor = 'I-500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)


    elif pitch >= 5:
        movePmotor = 'I250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
    elif pitch <= -5:
        movePmotor = 'I-250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
    elif roll >= 5:
        moveRmotor = 'I250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
    elif roll <= -5:
        moveRmotor = 'I-250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)

    elif pitch >= 2:
        movePmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
    elif pitch <= -2:
        movePmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
    elif roll >= 2:
        moveRmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
    elif roll <= -2:
        moveRmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)

    elif pitch <= 1:
        movePmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
    elif pitch >= -1:
        movePmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
    elif roll <= 1:
        moveRmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
    elif roll >= -1:
        moveRmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)

    while pitch > 0.000001 or pitch < 0.000001:
        if pitch > 0.000001:
            movePmotor = 'I1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
            outP.write(bytes(movePmotor, 'utf-8'))
            time.sleep(5)
        else:
            movePmotor = 'I-1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
            outP.write(bytes(movePmotor, 'utf-8'))
            time.sleep(5)

    while roll > 0.000001 or roll < 0.000001:
        if roll > 0.000001:
            moveRmotor = 'I1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
            out.write(bytes(moveRmotor, 'utf-8'))
            time.sleep(5)
        else:
            moveRmotor = 'I-1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
            out.write(bytes(moveRmotor, 'utf-8'))
            time.sleep(5)


while True:
    try:
        dynamic_balance()
    except KeyboardInterrupt:
        sys.exit(-1)
