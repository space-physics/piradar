#!/usr/bin/env python
"""
This function simulates the relatively devastating effects of ADC clipping, particular from power-line sources.
A pulse train in the time-domain is frequency replication in the time domain, from basic Fourier analysis.

This empirical model is based on observations with Red Pitaya and 2 meter piece of wire put in center 
conductor of "IN1" SMA with jumpers set to LV inside a commercial building, where it appears that
60 Hz is being picked up and is overloading the analog input chain.
"""
import numpy as np
import scipy.signal as signal
from matplotlib.pyplot import figure,show

Asig = 5
t0 = 0.
t1 = 0.1
fc = 10e3 # [Hz] carrier frequency
fs = 100000 # [Hz] sampling frequency

Ajam =.3
fjam = 60. # [Hz]

t = np.arange(t0,t1,1/fs)

sig = Asig * np.cos(2*np.pi*fc*t)
#jam = Ajam * np.cos(2*np.pi*fjam*t)
jam = Ajam * signal.square(2*np.pi*fjam*t)
jam[jam<0] = 0.5*Ajam

sigclip = (sig * jam).clip(-1,1)

#%%
ax = figure().gca()
ax.plot(t,sigclip)
ax.set_xlabel('time [sec]')
ax.set_ylabel('amplitude')

twin = 0.1 # [sec] window length
f,Sxx = signal.welch(sigclip, fs, nperseg=int(twin*fs),)

ax = figure().gca()
ax.plot(f, 10*np.log10(Sxx))
ax.set_ylim((-100,None))

show()