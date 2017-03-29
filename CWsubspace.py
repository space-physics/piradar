#!/usr/bin/env python
"""
When sinusoid frequency separation is small, you can run out of RAM by zero-padding.
Another, faster technique for this case is subspace methods such as Root-MUSIC and ESPRIT.
Michael Hirsch, Ph.D.
"""
from numpy import arange,pi,sin
from numpy.random import normal
from matplotlib.pyplot import figure,show

# recall DFT is samples of continuous DTFT
zeropadfactor = 3 #arbitrary, expensive way to increase DFT resolution. 
# eventually you'll run out of RAM if you want arbitrarily high precision

fb0 = 1. # Hz  arbitrary "true" Doppler frequency saught.
t1 = 2.  # final time, t0=0 seconds
An = 0.1 # standard deviation of AWGN

ft = 15e3 # [Hz]
At = 0.5

fb = ft + fb0 # [Hz]
Ab = 0.1

fs = 100e3 # [Hz]
t = arange(0, t1-1/fs, 1/fs)

xt = At*sin(2*pi*ft*t)
xbg = xt + normal(0., An, xt.shape) # we receive the transmitter with noise
#%% simulated target beat signal (noise free)
xb = Ab*sin(2*pi*fb*t)
#%% compute noisy, jammed observatoin
y = xb + xbg + normal(0., An, xbg.shape) # each time you receive, we assume i.i.d. AWGN
#%% plots
ax = figure().gca()
ax.plot(t,y)
ax.set_xlabel('time [sec]')
ax.set_ylabel('amplitude')
ax.set_title('Noisy, jammed receive signal')

show()
