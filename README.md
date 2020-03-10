# WWV Multipath
Aidan Montare

**Current project status:** I made a draft version of the code. No clue if it works with the Rigol scope correctly or not.

![Scope display](scope2.bmp)

*The above image is from the "UltraScope" software from Rigol ([available
free on their website](https://www.rigolna.com/products/digital-oscilloscopes/1000/)).
If you want to manually use your computer to control your scope, this is a
good option.*

## Background

## Equipment
- HF antenna suitable for receiving WWV / WWVH
- AM radio receiver
- GPS-Disciplined Oscillator (GPSDO)
- Rigol DS1000E series oscilloscope (we used a DS1102E)
- appropriate cabling to connect audio output of AM receiver to 
one channel of the oscilloscope
- appropriate cabling to connect GPSDO 1 PPS output to a different
channel of the oscilloscope
- USB B to USB A cable
- computer

## Dependencies
- Python 3
- usual SciPy things (numpy, matplotlib)
- [PyVisa](https://pyvisa.readthedocs.io/en/latest/index.html)
(available via pip)
- Rigol drivers (on the [Rigol page for the scope]
(https://www.rigolna.com/products/digital-oscilloscopes/1000/), download
the "UltraSigma Instrument Connectivity Driver")

## Setup

1. Connect all the things. Install the dependencies.
2. Get the oscilloscope triggering happily off the PPS signal. Verify
you can see the second ticks arriving (as in image above).
3. Run `collect.py`, and data should start flowing!

## References

The Rigol Programming Guide (under the manuals section on their website)
is quite helpful.

http://notes.theorbis.net/2010/05/creating-time-lapse-with-ffmpeg.html
