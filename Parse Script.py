"""
    File: Parse Script.py
    Author: Bob Wei
    Created On: 11/10/2016
    Desc: Parses the raw data obtained from an oscilloscope and creates a new data file 
"""

import os
import matplotlib.pyplot as plt
import numpy 

num_values = 4000
#Lists for storing x,y,and z data
x_values = []
y_values = []
z_values = []
time_values = []


filename = 'test1.dat'
#=============================================================================
#defined function for parsing file data
#=============================================================================
def parse_debug_values ():
    #opens file in read mode as 'values'
    with open(filename, 'r') as values:
        #loops through each line in file
        for line in values:
            
            #bypasses blank lines
            if line.strip():
                #print((line.split('a')[0]))
                #parses each value with split and strip functions into int
                x_values.append(int((line.split('a')[1]).strip('X=')))
                y_values.append(int((line.split('a')[2]).strip('Y=')))
                z_values.append(int((line.split('a')[3]).strip('Z=')))
                time_values.append(float((line.split('a')[0])))
                
#=============================================================================
#calls function
if os.path.isfile(filename): parse_debug_values()

#=============================================================================
# CODE BELOW provides a plot of the data before writing the parsed data to file
#=============================================================================

x_total = 0
y_total = 0
z_total = 0

for i in range(round(num_values*0.9), num_values):
    x_total += x_values[i]
    y_total += y_values[i] 
    z_total += z_values[i] 

x_base = x_total/round(num_values * 0.1)
y_base = y_total/round(num_values * 0.1)
z_base = z_total/round(num_values * 0.1)

x_abs = []
y_abs = []
z_abs = []

for j in range(0,num_values):
    x_abs.append(x_values[j] - x_base)
    y_abs.append(y_values[j] - y_base)
    z_abs.append(z_values[j] - z_base)

a_values = numpy.sqrt(numpy.add(numpy.add(numpy.power(x_abs,2),numpy.power(y_abs,2)),numpy.power(z_abs, 2)))

file = open ('accelerometerTest2.dat', 'w')
    
for i in range(0, num_values):
    file.write ('{}\t'.format(time_values[i]))
    file.write ('{}\n'.format(y_abs[i]))
    
file.close()

plt.subplot(4, 1, 1)
plt.title("X-Values");
plt.xlabel(r's')
plt.plot(time_values, x_abs)
plt.show()

plt.subplot(4, 1, 2)
plt.title("Y-Values");
plt.xlabel(r's')
plt.plot(time_values, y_abs)
plt.show()

plt.subplot(4, 1, 3)
plt.title("Z-Values");
plt.xlabel(r's')
plt.plot(time_values, z_abs)
plt.show()

plt.subplot(4, 1, 4)
plt.title("X+Y+Z-Values");
plt.xlabel(r's')
plt.plot(time_values, a_values)
plt.show()
