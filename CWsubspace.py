#!/usr/bin/env python
"""
When sinusoid frequency separation is small, you can run out of RAM by zero-padding.
Another, faster technique for this case is subspace methods such as Root-MUSIC and ESPRIT.
Michael Hirsch, Ph.D.
"""
from math import pi,ceil
from numpy import arange,sin
from numpy.random import normal
from scipy.signal import welch
from matplotlib.pyplot import figure,show

# recall DFT is samples of continuous DTFT
zeropadfactor = 1 #arbitrary, expensive way to increase DFT resolution. 
# eventually you'll run out of RAM if you want arbitrarily high precision

fs = 10e3 # [Hz]
fb0 = 2. # Hz  arbitrary "true" Doppler frequency saught.
t1 = 1.  # final time, t0=0 seconds
An = 0.1 # standard deviation of AWGN

ft = 1.5e3 # [Hz]
At = 0.5

fb = ft + fb0 # [Hz]
Ab = 0.1

t = arange(0, t1-1/fs, 1/fs)

xt = At*sin(2*pi*ft*t)
xbg = xt + normal(0., An, xt.shape) # we receive the transmitter with noise
#%% simulated target beat signal (noise free)
xb = Ab*sin(2*pi*fb*t)
#%% compute noisy, jammed observatoin
y = xb + xbg + normal(0., An, xbg.shape) # each time you receive, we assume i.i.d. AWGN
#%% time 
fg = figure(1); fg.clf()
ax = fg.gca()
ax.plot(t,y)
ax.set_xlabel('time [sec]')
ax.set_ylabel('amplitude')
ax.set_title('Noisy, jammed receive signal')
#%% periodogram
dt = 0.45  #seconds between time steps to plot (arbitrary)
dtw = 2*dt #  seconds to window
tstep = ceil(dt*fs)
wind = ceil(dtw*fs);
Nfft = zeropadfactor*wind
 
fg = figure(3); fg.clf()
ax = fg.gca()

f,Sraw = welch(y,fs,nperseg=wind,noverlap=tstep,nfft=Nfft);
ax.plot(f,Sraw,'r',label='raw signal')

ax.set_xlim([1400,1600])
ax.set_xlabel('frequency [Hz]')
ax.set_ylabel('amplitude')
ax.legend()

show()
