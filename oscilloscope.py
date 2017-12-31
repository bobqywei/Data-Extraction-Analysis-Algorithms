# -*- coding: utf-8 -*-
"""
    File: oscilloscope.py
    Author: Bob Wei
    Created On: 8/2/2016
    Desc: This file reads data from a GWINSTEK GDS-1002A Oscilloscope and plots the data.
"""

import serial
import sys
import numpy
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 0, barLength = 50):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


port = "COM4"
baudrate = 115200
ser = serial.Serial(port, 
                    baudrate, 
                    parity = serial.PARITY_NONE, 
                    stopbits = serial.STOPBITS_ONE, 
                    bytesize = serial.EIGHTBITS, 
                    xonxoff = False, 
                    rtscts = False, 
                    dsrdtr = False, 
                    timeout = 30) 
# ---------------------------------------------------------------------------
# Get the model name and number from the oscilloscope
#
ser.write('*idn?\n'.encode())
scope_name_string = ser.readline().decode ("utf-8").strip('\n')
print("SCOPE READER     :")
print("SCOPE NAME       :",scope_name_string )

# ---------------------------------------------------------------------------
# Request the data stored in oscilliscope memory
#
ser.write(':acquire1:lmemory?\n'.encode())

# --------------------------------
# First byte shoud be a hash
#
hash_mark = ser.read(1)
if (hash_mark == b'#'): 
    print("DATA CHECK       : Hash mark seen")
else: 
    print("DATA CHECK       :Error - has mark not seen")
    ser.close(); sys.exit()
    
# --------------------------------
# Read the data size digit
#
data_size_digit = ser.read(1)
if (data_size_digit == b'4'): 
    print("DATA SIZE DIGIT  : 4")
elif (data_size_digit == b'7'): 
    print("DATA SIZE DIGIT  : 7")
else:    
    print("DATA SIZE DIGIT  : Data size digit not read")
    ser.close(); sys.exit()
    
# --------------------------------
# Read the data size 
# 
data_size_string = ser.read(int(data_size_digit))
data_size = 0
if (data_size_string == b'8008'):
    print("DATA SIZE        : 4k points")
    data_size = 4000
elif (data_size_string == b'2000008'):
    print("DATA SIZE        : 1M points")
    data_size = 1000000
elif (data_size_string == b'4000008'):
    print("DATA SIZE        : 2M points")
    data_size = 2000000
else:
    print("DATA SIZE        : Error - data size not read")
    ser.close(); sys.exit()

# --------------------------------
# Read the time interval
# 
time_interval_string = ser.read(4)
time_interval_string = time_interval_string[::-1]
time_interval = numpy.frombuffer(time_interval_string, dtype=numpy.float32)
print("TIME INTERVAL    :", time_interval[0]," sec")

# --------------------------------
# Read the channel number of the data
#
channel_number = ser.read(1)
if (channel_number == b'\x01'):
    print("CHANNEL NUMBER   : 1")
elif (channel_number == b'\x02'):
    print("CHANNEL NUMBER   : 2")
else:
    print("CHANNEL NUMBER   : Error - channel not found")
    ser.close(); sys.exit()

# --------------------------------
# Empty 3 bytes
#
ser.read(3)

# --------------------------------
# Data Collection
#
data = numpy.empty([data_size,],dtype=numpy.int16)
for i in range(data_size):
    buffer = ser.read(2)
    data[i] = numpy.frombuffer(buffer, dtype=numpy.int16)
    if (i%1000 == 0) : printProgress(i,data_size)
    #--- END FOR i ---
print('\n')


# ---------------------------------------------------------------------------
# Get voltaage scale and probe type
#
ser.write(':channel1:scale?\n'.encode())
scale_string = ser.readline().decode ("utf-8").strip('\n')
scale = float(scale_string)
print("SCALE            :", scale, "volts/div")
ser.write(':channel1:probe:type?\n'.encode())
print("PROBE TYPE       :", ser.readline().decode ("utf-8").strip('\n'))

data = data/(256*25/scale)
# ---------------------------------------------------------------------------
# Close the serial port
#
print("SCOPE READER     : Done")
ser.close()

# ---------------------------------------------------------------------------
# Plot the data in interactive terminal
#
plt.plot(data)
plt.show()

# ---------------------------------------------------------------------------
# Save data to file.
#
fd = open('test1.dat', 'w')
for i in range(data_size):
   string = repr(i*time_interval[0])+' \t'+repr(data[i])+'\n'
   fd.write(string)
fd.close()

