#############################################################################
# Program: CSACS_v4.1.py
# Author: Larry Hensley (Based on code written by Nicholas R. Tibbetts and Mark R. Mercier)
# Email: markrm33@vt.edu
# Required Python Version: 3.4 or greater
# Version: 4.0
# Date: 30MAR17
#
# Program Description: Graphical User Interface and control of the 
#   Virginia Tech CubeSat Attitude Control Simulator
#
# Version History
#   0.1: Basic GUI Structure and Functionality (10JAN15)
#   0.2: Added Updating VectorNav VN-100 Functionality (21JAN15)
#   0.3: Added Pitch, Roll, Yaw History Plotting Functionality (25FEB15)
#   0.4: Added Updating Motor Position Functionality (23MAR15)
#   0.5: Added Input Control Capabilities (01APR15)
#   1.0: Release Version
#   3.0: Added Angular Rate graph and cleaned up GUI format (06JUL16)
#   4.0: Ported to run on BeagleBone Black
#
#
#############################################################################
#
# The following two websites are recommended for getting caught up to
# speed in learning Python:
#
# www.pythonprogramming.net (also, Sentdex YouTube channel)
# www.codecademy.com
#
#############################################################################
#
# These are the modules, or sub-programs, that Python needs to have 
#    access to for everything to work.  With the exception of vn.core, 
#    modules can be installed (on Windows) by opening the command prompt 
#    and issuing the following command after the >:
#
#    C:\Python34> python -m pip install <<Module Name>>
#
#    For further details, a web search of 'installing python modules with 
#    pip on Windows' will yield understanding. """
#
#############################################################################  

from vnpy import *           #Core Library for VN-100 interfacing

import serial

import os, re, datetime, time, sched            #Importing modules used for time formatting and system information
from datetime import timedelta

#############################################################################

vs = VnSensor()
vs.connect("/dev/ttyUSB1",115200)

outP = serial.Serial(port="/dev/ttyUSB0", baudrate=57600, bytesize=8, parity='N', stopbits=1, timeout=2 ) # Pitch Motor
out = serial.Serial(port="/dev/ttyUSB2", baudrate=57600, bytesize=8, parity='N', stopbits=1, timeout=2 ) # Roll Motor

def dynamic_balance():
    pry = vs.read_yaw_pitch_roll()       
    pitch = round(pry.y,8)
    roll = round(pry.z,8)

    print(pitch)
    print(roll)

    pitchCorrection = 500*pitch**3
    movePmotor = 'I'+str(int(round(pitchCorrection)))+',25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
    outP.write(bytes(movePmotor, 'utf-8'))

    rollCorrection = 500*roll**3
    moveRmotor = 'I'+str(int(round(rollCorrection)))+',25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
    out.write(bytes(moveRmotor, 'utf-8'))

    time.sleep(5)

while True:

	dynamic_balance()
