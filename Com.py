"""
    File: Com.py
    Author: Bob Wei
    Created On: 10/15/2016
    Description: Multiple threaded program designed to configure and extract output data from a ST Microelectronics LIS2HH12 accelerometer attached to
                 a STEVAL-MKI164V1 adapter/evaluation board
"""

#imports necessary libraries
import serial
import threading
import time
from queue import Queue
import numpy

#============================================================================
#forms the directory of the file 
file_name = 'comv4test'
#opens new file or appends onto existing file
#if os.path.isfile(file_name):
 #   file  = open(file_name, 'a')
#else:
file = open(file_name + '.dat', 'wb')
timepoints_file = open(file_name + '_timepoints.dat', 'w')
#============================================================================
#initializes the serial port settings
port = "COM3"
baudrate = 115200
ser = serial.Serial(port, baudrate, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS, xonxoff = False, rtscts = False, dsrdtr = False) 
#============================================================================

print(ser.isOpen(),'\n')   ## ----> to check and make sure (should say True)
# Write the commands to choose the correct software:
ser.write(b'*setdb164v1\r')
ser.write(b'*Zoff\r')
ser.write(b'*echoon\r')
ser.write(b'*w2047\r')
ser.readline() ### ----> to read over the register response before debug is called
ser.write (b'*dev\r')
print(ser.readline())

#list for multiple threads
num_data = 2000
timepoints = [None] * num_data
data = [None] * num_data
#============================================================================
# This is the code for listening thread.
def read_from_port(ss,data_count,q_in):
    #counter variable used to keep track of the number of lines of data
    index = 1
    print('Listening thread is running: \n')
    start_time = time.clock()
    
    #loops for a designated number of times (data_count)
    while index <= data_count:
        #decodes the line of data retrieved 
        ss.read(6)
        buffer = ss.read(13)
        data[index-1] = buffer
        timepoints[index-1] = time.clock()-start_time
        
        #increases the counter
        index += 1
        #stores the current value of the index into the queue so that it can be accessed by the other thread
        q_in.put(index)
        
#============================================================================
#This is the code for the monitoring thread
def monitor_port (q_out):
    #infinite loop that will constantly monitor the status of the listening thread
    while True:
        #compares the value stored in the queue to the limit set by the user
        if q_out.get() > num_data:
            #closes the serial connection and the file
            ser.write(b'*stop\r')
            ser.close()
            print('Serial Closed')
            
            for i in range(0,num_data):
                print(timepoints[i])
                timepoints_file.write('{}\n'.format(timepoints[i]))
                file.write(data[i])
            
            
            file.close()
            
            # exits the infinite loop
            return
#============================================================================
#initializes the queue
q = Queue()
#initializes the thread and arguments
t = threading.Thread(target = read_from_port, args = (ser,num_data,q,))
t2 = threading.Thread(target = monitor_port, args = (q,))
#executes thread t
t.start()
t2.start()

#begins data collection
ser.write(b'*start\r')
ser.read(14)
#ser.write(b'*start\r')
