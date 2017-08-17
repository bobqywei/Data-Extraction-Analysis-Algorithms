# -*- coding: utf-8 -*-
"""
    File: frequency_analysis.py
    Created on: Tue Oct 25 15:05:02 2016
    Author: Bob Wei
    Description: Program uses fourier transform to remove unwanted frequencies from a data set (obtained from oscilloscope.py)
"""
import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import os.path
import time
#===============================================================================
def nextpower2(n):
    m_f = np.log2(n)
    m_i = np.ceil(m_f)
    return 2**m_i

#===============================================================================
filename = 'testvalues.dat'
data = np.loadtxt(filename)
number_of_timepoints = data.shape[0] # obtains number of time/data points in dataset
print('Number of data points: ', number_of_timepoints)

timepoints = data[:,0]
timestep = timepoints[1]-timepoints[0] # obtains timestep in micro s between each time/data point
print('Timestep: ', timestep*math.pow(10,6), 'micro-s')

voltagepoints = data[:,1] # obtains actual voltage values  

# plots original data
plt.subplot(2, 1, 1)
plt.title("original data");
plt.xlabel(r's')
plt.plot(timepoints,voltagepoints)
plt.show()

#plt.waitforbuttonpress()
plt.close()

# allows user to select the time point of the initial trigger and to omit all prior data points
start_time = float(input('Enter start timepoint: '))
print('\nStart timepoint: ', start_time, 's')

# cuts the data points from the selected time point
cut_timepoints = timepoints[(timepoints >= start_time)]
cut_voltagepoints = voltagepoints[(timepoints >= start_time)]
# readjusts number of data points
number_of_timepoints = len(cut_timepoints)
print('Number of remaining data points: ', number_of_timepoints)

#===============================================================================
# carries out fourier transform on the selected data
ftlength      = int(nextpower2(number_of_timepoints))
voltagesFT  = np.fft.fft(cut_voltagepoints,n=ftlength)
voltagesFT_magnitude = np.multiply(voltagesFT,np.conjugate(voltagesFT))
frequencies   = np.fft.fftfreq(ftlength, d=timestep)

# selectively cuts out certain frequencies from the fourier transform based on the situation
for i in range(len(frequencies)):
    if math.fabs(frequencies[i]) > 8000:
        voltagesFT[i] = 0
        voltagesFT_magnitude[i] = 0

# carries out inverse fourier transform
voltagesIFT = np.fft.ifft(voltagesFT,n=ftlength)

# plots the data after being cut from the selected start time point
plt.subplot(3, 1, 1)
plt.title("cut data");
plt.xlabel(r's')
plt.plot(cut_timepoints, cut_voltagepoints)
plt.show()

# plots the fourier transform
plt2 = plt.subplot(3, 1, 2)
plt.title("magnitude of fft");
plt.xlabel(r'Hz')
plt.plot(frequencies,voltagesFT_magnitude)
plt2.set_xlim([-100000,100000])
plt.show()

# plots the original data after the omission of certain frequencies and inverse fourier transform
plt.subplot(3, 1, 3)
plt.title("reconstructed data from inverse fft, dominant peaks removed");
plt.xlabel(r's')
plt.plot(cut_timepoints,voltagesIFT[:2349])    #gives a warning about discarding imaginary part of complex number because IFT is complex.
plt.show()
