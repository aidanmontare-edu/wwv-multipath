# -*- coding: utf-8 -*-
"""
Collects WWV Multipath data from Rigol DS1000E series oscilloscopes.


Created on Wed Mar  4 14:08:11 2020

@author: Aidan Montare <aam141@case.edu>

Based on
http://www.righto.com/2013/07/rigol-oscilloscope-hacks-with-python.html
and
https://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/
"""

import pyvisa
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plot

rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
usb = tuple(filter(lambda x: 'USB' in x, instruments))
if len(usb) != 1:
    print('Bad instrument list', instruments)
    sys.exit(-1)
scope = rm.open_resource(usb[0], timeout=20, chunk_size=1024000) # bigger timeout for long mem

print('Device in use:')
print(scope.query("*IDN?"))

# Grab the raw data from channel 1
scope.write(":STOP")
 
# Get the timescale
timescale = scope.query_ascii_values(":TIM:SCAL?")[0]

# Get the timescale offset
timeoffset = scope.query_ascii_values(":TIM:OFFS?")[0]
voltscale = scope.query_ascii_values(':CHAN1:SCAL?')[0]

# And the voltage offset
voltoffset = scope.query_ascii_values(":CHAN1:OFFS?")[0]

scope.write(":WAV:POIN:MODE RAW")
rawdata = scope.query_binary_values(":WAV:DATA? CHAN1")[10:]
data_size = len(rawdata)
sample_rate = scope.query_ascii_values(':ACQ:SAMP?')[0]
print('Data size:', data_size, "Sample rate:", sample_rate)

scope.write(":RUN")
scope.close()

data = np.array(rawdata)

# Walk through the data, and map it to actual voltages
# This mapping is from Cibo Mahto
# First invert the data
data = data * -1 + 255
 
# Now, we know from experimentation that the scope display range is actually
# 30-229.  So shift by 130 - the voltage offset in counts, then scale to
# get the actual voltage.
data = (data - 130.0 - voltoffset/voltscale*25) / 25 * voltscale

# Now, generate a time axis.
time = np.linspace(timeoffset - 6 * timescale, timeoffset + 6 * timescale, num=len(data))
 
# See if we should use a different time axis
if (time[-1] < 1e-3):
    time = time * 1e6
    tUnit = "uS"
elif (time[-1] < 1):
    time = time * 1e3
    tUnit = "mS"
else:
    tUnit = "S"
 
# Plot the data
plot.plot(time, data)
plot.title("Oscilloscope Channel 1")
plot.ylabel("Voltage (V)")
plot.xlabel("Time (" + tUnit + ")")
plot.xlim(time[0], time[-1])
plot.show()
