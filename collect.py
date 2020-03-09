# -*- coding: utf-8 -*-
"""
Collects raw data of channels 1 and 2 from Rigol DS1000E series oscilloscopes.

Also records a metadata file with timescale and voltagescale
information to allow other programs to interpret the raw data.

Do not adjust the oscilloscope controls while the program is running.

@author: Aidan Montare <aam141@case.edu>

Based on
http://www.righto.com/2013/07/rigol-oscilloscope-hacks-with-python.html
and
https://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/
"""

import pyvisa
import sys
import time
import datetime
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plot

def readWaveform(scope, channel):
    """
    Read the raw waveform from the given scope and channel
    
    scope: the opened scope resource
    channel: an integer channel number
    
    returns: the raw data
    """
    scope.write(":STOP")
    
    scope.write(":WAV:DATA? CHAN" + str(channel))[10:]
    rawdata = scope.read_raw()
    
    scope.write(":RUN")
    return rawdata

rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
usb = tuple(filter(lambda x: 'USB' in x, instruments))
if len(usb) != 1:
    print('Bad instrument list', instruments)
    sys.exit(-1)
scope = rm.open_resource(usb[0], timeout=20, chunk_size=1024000) # bigger timeout for long mem

print('Device in use:')
scope_name = scope.query("*IDN?")
print(scope_name)

# configure scope

scope.write(":WAV:POIN:MODE RAW")

# Get metadata

timescale = scope.query_ascii_values(":TIM:SCAL?")[0]
timeoffset = scope.query_ascii_values(":TIM:OFFS?")[0]

voltscale = [scope.query_ascii_values(':CHAN1:SCAL?')[0],
             scope.query_ascii_values(':CHAN2:SCAL?')[0]]
voltoffset = [scope.query_ascii_values(":CHAN1:OFFS?")[0],
              scope.query_ascii_values(":CHAN2:OFFS?")[0]]

samplerate = scope.query_ascii_values(':ACQ:SAMP?')[0]

metadata = {"timescale": timescale, "timeoffset": timeoffset,
            "voltscale": voltscale, "voltoffset": voltoffset,
            "samplerate": samplerate}


# the last datetime for which we recorded data
lastSecondRecorded = (datetime.datetime.now(datetime.timezone.utc)
                     .replace(microsecond=0))

try:
    # The main loop runs continuously, but useful code is only
    # executed if the current UTC second is more than half over
    # and we have not recorded data for this second yet.
    # This translates to recording data once a second at the half-
    # second mark.
    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        
        if now > now.replace(microsecond=500000) and \
        now.replace(microsecond=0) > lastSecondRecorded:
            print("recording data for", now.isoformat(), end="\t[")
            lastSecondRecorded = now.replace(microsecond=0)
            
            # read and record data for each channel
            for channel in [1, 2]:
                rawdata = readWaveform(scope, channel)
                filename = now.strftime("%Y-%m-%dT%H-%M-%S%Z") + \
                    "chan" + str(channel) + ".bin"
                
                with open(filename, "wb") as f:
                    f.write(rawdata)
                print("*", end="")
            
            # check if we ran too long
            check = datetime.datetime.now(datetime.timezone.utc)
            if check.replace(microsecond=0) > lastSecondRecorded:
                print('\nRead operation took too long: possible data errors in the last set of files')
                sys.exit(-1)
            
            metadata_filename = now.strftime("%Y-%m-%dT%H-%M-%S%Z") + ".json"
            
            with open(metadata_filename, "w") as f:
                json.dump(metadata, f, indent=1)
                f.write("\n")
            print("*]")
            
        else:
            None
        time.sleep(.1)
except KeyboardInterrupt:
    # If the user interrupts the program, end gracefully.
    print("Ending collection...", end="")
    scope.close()
    print("Scope closed.")
    