#############################################################################
# Program: CSACS_v3.0.py
# Author: Mark R. Mercier (Based on code written by Nicholas R. Tibbetts)
# Email: markrm33@vt.edu
# Required Python Version: 3.4 or greater
# Version: 3.0
# Date: 06JUL16
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

from vn.core import *           #Core Library for VN-100 interfacing

from tkinter import *           #TKinter module for GUI 
from tkinter.ttk import Style

import os, re, datetime, time, sched            #Importing modules used for time formatting and system information
from datetime import timedelta

import pandas as pd                             #Import pandas module for improved data structures
from pandas import DataFrame
import pandas_datareader

import numpy as np                              #Import NumPy for scientific computing capabilities

import matplotlib                               #Import matplotlib for plotting capabilities
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.dates as mdates
matplotlib.use("TkAgg")         #Must be placed before matplotlib.pyplot import or will have no effect
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

#############################################################################


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
vs.connect("COM3",115200)

""" Connect to Haydon-Kerk Motors and Motor Controllers """
import serial
outP = serial.Serial(port="COM4", baudrate=57600, bytesize=8, parity='N', stopbits=1, timeout=2 ) # Pitch Motor
out = serial.Serial(port="COM5", baudrate=57600, bytesize=8, parity='N', stopbits=1, timeout=2 ) # Roll Motor

## Check if connected (DEBUG ONLY)
# outP.isOpen()
# out.isOpen()


""" Graphics Options """

LARGE_FONT = ("Verdana", 12) # Change this, just defining some new font to use in our labels
style.use("bmh")

fig = Figure(figsize = (7,9), dpi = 100,frameon=False) # Add the canvas
fig.suptitle('Live Accelerometer Graph',fontsize=14)
a = fig.add_subplot(211)
b = fig.add_subplot(212)

""" Set up our animation function.  This has to be located here for whatever reason to work.
    The animate function collects data and plots it in real time so the user can observe
    the time history and current relative angular location of the air bearing. """ 

def quit_func():
    quit()

def animate(i):

    """ Grab and Store Data """

    def get_time():
        current_time.append(datetime.datetime.now().time())
    get_time()
    
    def read_pitch():
        pry = vs.readYawPitchRoll()        
        pitch_history.append(round(pry.y,5))
    read_pitch()

    def read_roll():
        pry = vs.readYawPitchRoll()
        roll_history.append(round(pry.z,5))
    read_roll()

    def read_yaw():
        pry = vs.readYawPitchRoll()
        yaw_history.append(round(pry.x,5))
    read_yaw()

    def read_pitch_rate():
        pry_rate = vs.readAngularRateMeasurements()
        pitch_rate_history.append(round(pry_rate.y,5))
    read_pitch_rate()

    def read_roll_rate():
        pry_rate = vs.readAngularRateMeasurements()
        roll_rate_history.append(round(pry_rate.x,5))
    read_roll_rate()    

    def read_yaw_rate():
        pry_rate = vs.readAngularRateMeasurements()
        yaw_rate_history.append(round(pry_rate.z,5))
    read_yaw_rate()


    """Time Calculations"""
    graph_length = 50 #In Seconds
    current_seconds = []
    for t in current_time:
        current_seconds.append(t.hour*3600+t.minute*60+t.second+t.microsecond/1000000-(current_time[0].hour*3600+current_time[0].minute*60+current_time[0].second+current_time[0].microsecond/1000000))

    """ Plot Data """
    a.clear()  ## Clear Graph -- Saves processor memory
    a.plot(current_seconds, pitch_history, label = 'Pitch')
    a.plot(current_seconds, roll_history, label = 'Roll')
    a.plot(current_seconds, yaw_history, label = 'Yaw')

    b.clear()
    b.plot(current_seconds,pitch_rate_history,label = 'Pitch Rate')
    b.plot(current_seconds,roll_rate_history,label = 'Roll Rate')
    b.plot(current_seconds,yaw_rate_history,label = 'Yaw Rate')

    """ Plotting Options """
    
    a.set_title('Angular Position vs. Time')
    a.xaxis.set_major_formatter(mticker.ScalarFormatter())
    a.set_ylabel('Angular Position (\u00b0)')
    a.set_xlabel('')
    for label in a.xaxis.get_ticklabels(): # Rotates time labels by 45 Deg
        label.set_rotation(45)
    plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
    a.set_autoscaley_on(True)
    a.set_ylim([-180,180])
    a.set_autoscalex_on(True)
    if len(current_seconds)>graph_length:
        a.set_xlim([current_seconds[-graph_length],current_seconds[-1]])
    

    b.set_title('Angular Rate vs. Time')
    b.xaxis.set_major_formatter(mticker.ScalarFormatter())
    b.set_ylabel('Angular Rate (\u00b0/s)')
    b.set_xlabel('time (s)')
    for label in b.xaxis.get_ticklabels():
        label.set_rotation(45)
    plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
    b.set_autoscaley_on(True)
    b.set_ylim([-180,180])
    b.set_autoscalex_on(True)
    if len(current_time)>graph_length:
        b.set_xlim([current_seconds[-graph_length],current_seconds[-1]])

""" Create the base class for the graphic interface window.  The CSACS class is the base class
    that all other windows are built on.  

    Taken from http://pythonprogramming.net/object-oriented-programming-crash-course-tkinter/
    Follow the youtube video from sentdex to understand what we are doing here """

class CSACS(Tk):

    """ This is the baseline for our tkinter window.  Understanding this is crucial to understanding how the GUI operates """ 

    def __init__(self, *args, **kwargs): # initialize our class
        
        Tk.__init__(self, *args, **kwargs) # initialize tkinter

        Tk.iconbitmap(self,default='AOE_Logo.ico')
        Tk.wm_title(self, "CSACS Control Software") # Application title
        
        container = Frame(self) # make our frame
        container.pack(side="top", fill="both", expand = True) # fill the space we define, if extra space, expand from the top and fill
        container.grid_rowconfigure(0, weight=1) # minimum column = 0, no priority (weight = 1)
        container.grid_columnconfigure(0, weight=1) # minimum column = 0, no priority (weight = 1)

        self.frames = {} # Empty Dictionary, allows us to have multiple pages 
        frame = StartPage(container, self) # Initial page that we run, passing through container and self

        self.frames[StartPage] = frame # define StartPage as a page we want to run

        frame.grid(row = 0, column = 0, sticky = "nsew") # Placing the frame in the window at specified location

        self.show_frame(StartPage) # We want to start the program with our first page "StartPage"

    def show_frame(self, cont): # cont = controller

        frame = self.frames[cont]
        frame.tkraise() # raise the passed in page to the front


""" These are the all the functions that we need to run the program.  The StartPage class calls
    the functions that are defined here. """

def qf(param):
    print(param)


""" Rename File Name to Current Date and Time, Set File Location """

def save_data(): 
    ts = time.time()
    base_dir = filedialog.askdirectory()
    filename_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H%M')
    filename_base = os.path.join(base_dir, filename_time)
    filename = '%s.csv' % filename_base
    print("Saving Data...")
    df1 = DataFrame.from_items([('Pitch',pdx), ('Roll',pdy),('Yaw',pdz)]) 
    df1.stack(level=0, dropna = False) # Takes rows and converts to columns
    df1.to_csv(filename) # outputs to csv file

# Only do this if the Stop button has not been clicked
def dynamic_balance():
    pry = vs.readYawPitchRoll()       
    pitch = round(pry.y,8)
    roll = round(pry.z,8)

    if pitch >= 10:
        movePmotor = 'I500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif pitch <=-10:
        movePmotor = 'I-500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif roll >= 10:
        moveRmotor = 'I500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif roll <=-10:
        moveRmotor = 'I-500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()

        
    elif pitch >= 5:
        movePmotor = 'I250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif pitch <= -5:
        movePmotor = 'I-250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif roll >= 5:
        moveRmotor = 'I250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif roll <= -5:
        moveRmotor = 'I-250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
        
    elif pitch >=2:
        movePmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif pitch <=-2:
        movePmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif roll >=2:
        moveRmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif roll <=-2:
        moveRmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
        
    elif pitch <= 1:
        movePmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif pitch >= -1:
        movePmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        outP.write(bytes(movePmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif roll <= 1:
        moveRmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()
    elif roll >= -1:
        moveRmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
        out.write(bytes(moveRmotor, 'utf-8'))
        time.sleep(5)
        dynamic_balance()

        
    while pitch > 0.000001 or pitch < 0.000001:
        if pitch > 0.000001:
            movePmotor = 'I1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
            outP.write(bytes(movePmotor, 'utf-8'))
            time.sleep(5)
            dynamic_balance()
        else:
            movePmotor = 'I-1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
            outP.write(bytes(movePmotor, 'utf-8'))
            time.sleep(5)
            dynamic_balance()
    
    while roll > 0.000001 or roll < 0.000001:
        if roll > 0.000001:
            moveRmotor = 'I1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
            out.write(bytes(moveRmotor, 'utf-8'))
            time.sleep(5)
            dynamic_balance()
        else:
            moveRmotor = 'I-1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
            out.write(bytes(moveRmotor, 'utf-8'))
            time.sleep(5)
            dynamic_balance()
    dynamic_balance()

def read_all():

    def read_time():
        current_time.append(datetime.datetime.now().time())
    read_time()
            
    def read_pitch():
        pry = vs.readYawPitchRoll() # imported command from vn.core to read VectorNav VN-100
        pitch_history.append(round(pry.y,5))
    read_pitch()

    def read_roll():
        pry = vs.readYawPitchRoll()
        roll_history.append(round(pry.z,5))
    read_roll()

    def read_yaw():
        pry = vs.readYawPitchRoll()
        yaw_history.append(round(pry.x,5))
    read_yaw()

    def read_pitch_rate():
        pry_rate = vs.readAngularRateMeasurements()
        pitch_rate_history.append(round(pry_rate.y,5))
    read_pitch_rate()

    def read_roll_rate():
        pry_rate = vs.readAngularRateMeasurements()
        roll_rate_history.append(round(pry_rate.x,5))
    read_roll_rate()    

    def read_yaw_rate():
        pry_rate = vs.readAngularRateMeasurements()
        yaw_rate_history.append(round(pry_rate.z,5))
    read_yaw_rate()
    
running = True  # Global flag

def scanning():
    if running:
        dynamic_balance()
##        read_all()

    # After 1 second, call scanning again (create a recursive loop)
    app.after(5000, scanning)

def start():
    """Enable scanning by setting the global flag to True."""
    global running
    running = True
    scanning()

def stop():
    """Stop scanning by setting the global flag to False."""
    global running
    running = False
    scanning()

""" This is our main interface page.  All graphs, buttons, labels, and entry boxes are
    defined here.  This class is the first (and only) page that the CSACS class calls. """

class StartPage(Frame):

    def __init__(self, parent, controller): # define the page

        Frame.__init__(self,parent) # inherit from tkinter.Frame
     
        """ Create button, text, and entry widgets """
        
        # Create real time graph from matplotlib.animation
        label1 = Label(self, text = "Real Time Position of VectorNav", font = "Verdana 10 bold").grid(row = 0, column = 0, sticky = W, pady=4, padx=5)

        canvas = FigureCanvasTkAgg(fig,self)
        canvas.show()
        canvas.get_tk_widget().grid(row = 1, column = 0, rowspan = 9, columnspan = 7, sticky = W, padx = 10 )
    
        # Create Display for current angular position in Pitch, Roll, and Yaw

        def label_pitch_act(label):
            def read_pitch():
                pry = vs.readYawPitchRoll() # read in some orientation data from the sensor(pitch, roll, yaw)
                pitch = round(pry.y,5)
                w1 = Label(self, text = '%.2f' %pitch).grid(row=3,column=9,padx=10,pady=4)
                label.after(500,read_pitch)
                pitch_history.append(pitch)
            read_pitch()

        def label_roll_act(label):
            def read_roll():
                pry = vs.readYawPitchRoll()
                roll = round(pry.z,5)
                w2 = Label(self, text = '%.2f' %roll).grid(row=3,column=10,padx=10,pady=4)
                label.after(500,read_roll)
                roll_history.append(roll) 
            read_roll()

        def label_yaw_act(label):
            def read_yaw():
                pry = vs.readYawPitchRoll()
                yaw = round(pry.x,5)
                w3 = Label(self, text = '%.2f' %yaw).grid(row=3,column=11,padx=10,pady=4)
                label.after(500,read_yaw)
                yaw_history.append(yaw)
            read_yaw()

        def label_pitch_rate_act(label):
            def read_pitch_rate():
                pry_rate = vs.readAngularRateMeasurements()
                pitch_rate = round(pry_rate.y,5)
                w4 = Label(self,text='%.2f' %pitch_rate).grid(row=6,column=9,padx=10,pady=4)
                label.after(500,read_pitch_rate)
                pitch_rate_history.append(pitch_rate)
            read_pitch_rate()

        def label_roll_rate_act(label):
            def read_roll_rate():
                pry_rate = vs.readAngularRateMeasurements()
                roll_rate = round(pry_rate.x,5)
                w5 = Label(self,text='%.2f' %roll_rate).grid(row=6,column=10,padx=10,pady=4)
                label.after(500,read_roll_rate)
                roll_rate_history.append(roll_rate)
            read_roll_rate()

        def label_yaw_rate_act(label):
            def read_yaw_rate():
                pry_rate = vs.readAngularRateMeasurements()
                yaw_rate = round(pry_rate.z,5)
                w6 = Label(self,text='%.2f' %yaw_rate).grid(row=6,column=11,padx=10,pady=4)
                label.after(500,read_yaw_rate)
                yaw_rate_history.append(yaw_rate)
            read_yaw_rate()
            


        label2 = Label(self, text = "Current Angular Position",  font = "Verdana 10 bold").grid(row = 1, column = 9, columnspan=3,pady=4, padx=5)
        
        label_pitch = Label(self, text = "Pitch (deg)").grid(row = 2, column = 9, pady = 4)
        label_roll = Label(self, text = "Roll (deg)").grid(row = 2, column = 10, padx = 10, pady = 4)
        label_yaw = Label(self, text = "Yaw (deg)").grid(row = 2, column = 11, pady = 4)

        label3 = Label(self,text="Current Angular Rate", font = "Verdana 10 bold").grid(row = 4,column = 9,columnspan=3,pady=4,padx=5)

        label_pitch_rate = Label(self,text="Pitch Rate (deg/s)").grid(row=5,column=9,padx=10,pady=4)
        label_roll_rate = Label(self,text="Roll Rate (deg/s)").grid(row=5,column=10,padx=10,pady=4)
        label_yaw_rate = Label(self,text="Yaw Rate (deg/s)").grid(row=5,column=11,padx=10,pady=4)

        pitch_history = []
        roll_history = []
        yaw_history = []

        pitch_rate_history = []
        roll_rate_history = []
        yaw_rate_history = []
        
        label = Label(self)
        label_pitch_act(label)
        label_roll_act(label)
        label_yaw_act(label)
        label_pitch_rate_act(label)
        label_roll_rate_act(label)
        label_yaw_rate_act(label)
        
        # Create Mass Properties Entry Matrix

        """ These entry boxes are currently unused and are here for future systems identfication """
        
        label3 = Label(self, text = "Payload Characteristics", font = "Verdana 10 bold").grid(row = 0, column = 7, columnspan=2,sticky = W)
 
        label_mass = Label(self, text = "Mass (kg):").grid(row = 1, column = 7, sticky = N,pady=3,padx=5)
        label_MOI_X = Label(self, text = "MOI X (m):").grid(row = 2, column = 7, sticky = N,pady=3,padx=5)
        label_MOI_Y = Label(self, text = "MOI Y (m):").grid(row = 1, column = 8, sticky = N,pady=3,padx=5)
        label_MOI_Z = Label(self, text = "MOI Z (m):").grid(row = 2, column = 8, sticky = N, pady=3,padx=5)
        
        self.ent_mass = Entry(self).grid(row = 1, column = 7, sticky = S, pady=3,padx=5)
        self.ent_MOI_X = Entry(self).grid(row = 2, column = 7, sticky = S, pady=3,padx=5)
        self.ent_MOI_Y = Entry(self).grid(row = 1, column = 8, sticky = S, pady=3,padx=5) 
        self.ent_MOI_Z = Entry(self).grid(row = 2, column = 8, sticky = S, pady=3,padx=5)
        
        # Create display for current Linear Actuator position
        # This requires encoder to be enabled.  Future Release Version will have this included
        
        label4 = Label(self, text = "Current Linear Actuator Position",  font = "Verdana 10 bold").grid(row = 3, column = 7, columnspan=2,sticky = W, pady = 2, padx = 2)

        label_curact1 = Label(self, text = "Pitch Axis Actuator (mm)").grid(row = 4, column = 7, sticky = N)
        label_curact2 = Label(self, text = "Roll Axis Actuator (mm):").grid(row = 4, column = 8, sticky = N, padx = 2, pady = 2)

        label_disp_act = Label(self, text = "NaN").grid(row = 4, column = 7, sticky = S, padx = 2, pady = 2)
        label_disp_act = Label(self, text = "NaN").grid(row = 4, column = 8, sticky = S, padx = 2, pady = 2)

            
        # Create Manual Linear Actuator Control Entry Matrix
        label6 = Label(self, text = "Manual Linear Actuator Control",  font = "Verdana 12 bold").grid(row = 5, column = 7, columnspan=2,sticky = W, pady=2, padx=2)
        
        onevar = BooleanVar()
        onevar.set(False)
        
        self.act_man = Checkbutton(self, text="Activate Manual Control", variable=onevar, onvalue=True).grid(row=7, column = 7, columnspan=2,sticky=W)
        label_man1 = Label(self, text = "Input X (mm):").grid(row = 6, column = 7, sticky = N)
        label_man2 = Label(self, text = "Input Y (mm):").grid(row = 6, column = 8, sticky = N, padx = 2, pady = 2)

        self.entryx = Entry(self).grid(row = 6, column = 7, sticky = S)
        self.entryy = Entry(self).grid(row = 6, column = 8, sticky = S, padx = 2, pady = 2)


        def move_x(self):
            if onevar == True: 
                position_x = self.entryx.get()
                movePmotor = 'I'+position+',25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
                outP.write(bytes(movePMotor, 'utf-8'))
            else:
                print("Manual Control Disabled.")
 
        def move_y(self):
            if onevar == True:
                position_y = self.entryy.get()
                moveRmotor = 'I'+position+',25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
                out.write(bytes(moveRMotor, 'utf-8'))
            else:
                print("Manual Control Disabled.")

        
        # Create Linear Actuator Control Button for Above
        label7 = Label(self, text = "Linear Actuator Control",  font = "Verdana 10 bold").grid(row = 8, column = 7, columnspan=2, sticky = W, pady=2, padx=2)
        
        self.move_x_button = Button(self,
                                    text = "MOVE X",
                                    command = lambda: move_x(),
                                   ).grid(row = 9, column = 7, sticky = 'WE', padx = 5, pady = 3)
        self.move_y_button = Button(self,
                                    text = "MOVE Y",
                                    command = lambda: move_y(),
                                   ).grid(row = 9, column = 8, sticky = 'WE', padx = 5, pady = 3)

        
        # Create button to run and end program
        label8 = Label(self, text = "Control Panel",  font = "Verdana 14 bold").grid(row = 8, column = 9, columnspan=3,sticky = W, pady=2)
        self.run_button = Button(self, 
                                 text = "RUN", 
                                 command = lambda: dynamic_balance()
                                ).grid(row = 9, column = 9, sticky = 'WE', pady=3, padx=5)
        
        self.save_button = Button(self,
                                  text = "SAVE",
                                  command = lambda: save_data()
                                  ).grid(row = 9, column = 10, sticky = 'WE', pady=3, padx=5)

        self.stop_button = Button(self,
                                  text = "STOP",
                                  command = lambda: stop()
                                  ).grid(row = 10, column = 9, sticky = 'WE', pady=3, padx=5)
        
        self.end_button = Button(self, 
                                 text = "END",
                                 command = lambda: quit_func()
                                ).grid(row = 10, column = 10, sticky = 'WE', pady=3, padx=5)
        

""" These commands tell python to load the CSACS class (and subsequent StartPage class.  The
    animation function begins and updates every second (1000 ms).  The app.mainloop command
    tells Python to display the window."""

app = CSACS()
ani = animation.FuncAnimation(fig, animate, interval=500)
app.mainloop()























""" Below are substitute functions to test the CSACS.py program without using serial ports """

"""

##def animate(i):
##    line, = a.plot(np.random.rand(10))
##    a.set_ylim(0, 1)
##
##    def update(data):
##        line.set_ydata(data)
##        return line,
##
##    def data_gen():
##        while True: yield np.random.rand(10)
##
###    a.clear()    
##    a.plot()

##
##
##    fig, ax = plt.subplots()
##    xfmt = mdates.DateFormatter('%H:%M:%S')
##    ax.xaxis.set_major_formatter(xfmt)
##    # make matplotlib treat x-axis as times
##    ax.xaxis_date()
##
##    fig.autofmt_xdate(rotation=25)

##def gather_data():
##    
##    pdx = [] # Necessary to initialize array and allow for spacing between values
##    pdy = []
##    pdz = []
##    i = 0        # Initialize counter
##
##    for i in range(0,100):
##        pdx.append( i )
##        pdy.append( i )
##        pdz.append( i )
##        i+=1     # Increase step size by 1f
##
##    return pdx, pdy, pdz
##
##pdx, pdy, pdz = gather_data()


##def balance(self):
##    pry = vs.readYawPitchRoll()       
##    pitch = round(pry.y,8)
##    roll = round(pry.z,8)
##
####    print(pitch)
####    print(roll)
##
##    def dynamic_balance():
##        if pitch >= 10:
##            movePmotor = 'I500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            outP.write(bytes(movePmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif pitch <=-10:
##            movePmotor = 'I-500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            outP.write(bytes(movePmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif roll >= 10:
##            moveRmotor = 'I500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            out.write(bytes(moveRmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif roll <=-10:
##            moveRmotor = 'I-500000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            out.write(bytes(moveRmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##
##            
##        elif pitch >= 5:
##            movePmotor = 'I250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            outP.write(bytes(movePmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif pitch <= -5:
##            movePmotor = 'I-250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            outP.write(bytes(movePmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif roll >= 5:
##            moveRmotor = 'I250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            out.write(bytes(moveRmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif roll <= -5:
##            moveRmotor = 'I-250000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            out.write(bytes(moveRmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##            
##        elif pitch >=2:
##            movePmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            outP.write(bytes(movePmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif pitch <=-2:
##            movePmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            outP.write(bytes(movePmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif roll >=2:
##            moveRmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            out.write(bytes(moveRmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif roll <=-2:
##            moveRmotor = 'I-100000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            out.write(bytes(moveRmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##            
##        elif pitch <= 1:
##            movePmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            outP.write(bytes(movePmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif pitch >= -1:
##            movePmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            outP.write(bytes(movePmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif roll <= 1:
##            moveRmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            out.write(bytes(moveRmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##        elif roll >= -1:
##            moveRmotor = 'I-50000,25600,9600,16000,320000,800000,490,122,490,490,50,8\r'
##            out.write(bytes(moveRmotor, 'utf-8'))
##            time.sleep(5)
##            dynamic_balance()
##
##            
##        while pitch > 0.000001 or pitch < 0.000001:
##            if pitch > 0.000001:
##                movePmotor = 'I1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
##                outP.write(bytes(movePmotor, 'utf-8'))
##                time.sleep(5)
##                dynamic_balance()
##            else:
##                movePmotor = 'I-1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
##                outP.write(bytes(movePmotor, 'utf-8'))
##                time.sleep(5)
##                dynamic_balance()
##        
##        while roll > 0.000001 or roll < 0.000001:
##            if roll > 0.000001:
##                moveRmotor = 'I1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
##                out.write(bytes(moveRmotor, 'utf-8'))
##                time.sleep(5)
##                dynamic_balance()
##            else:
##                moveRmotor = 'I-1,25600,9600,16000,320000,800000,490,122,490,490,50,64\r'
##                out.write(bytes(moveRmotor, 'utf-8'))
##                time.sleep(5)
##                dynamic_balance()
##    dynamic_balance()

"""
