#!/usr/bin/env python
"""
When sinusoid frequency separation is small, you can run out of RAM by zero-padding.
Another, faster technique for this case is subspace methods such as Root-MUSIC and ESPRIT.
Michael Hirsch, Ph.D.
"""
from math import pi,ceil
import numpy as np
from scipy.signal import welch
from matplotlib.pyplot import figure,show
#
from spectral_analysis.importfort import fort
from spectral_analysis import esprit,rootmusic
Sc,Sr = fort()

# recall DFT is samples of continuous DTFT
zeropadfactor = 1 #arbitrary, expensive way to increase DFT resolution. 
# eventually you'll run out of RAM if you want arbitrarily high precision
DTPG = 0.45  #seconds between time steps to plot (arbitrary)

def cwsim(fs):
    """
    This is a simulation of a noisy narrowband CW measurement (any RF frequency)
    """
#%% user parameters (arbitrary)
    fb0 = 2. # Hz  arbitrary "true" Doppler frequency saught.
    t1 = 3.  # final time, t0=0 seconds
    An = 1e-1 # standard deviation of AWGN
    
    ft = 1.5e3 # [Hz]
    At = 0.5
    
    fb = ft + fb0 # [Hz]
    Ab = 0.1
    
    t = np.arange(0, t1-1/fs, 1/fs)
    
    xt = At*np.sin(2*pi*ft*t)
    xbg = xt + np.random.normal(0., An, xt.shape) # we receive the transmitter with noise
    #%% simulated target beat signal (noise free)
    xb = Ab*np.sin(2*pi*fb*t)
    #%% compute noisy, jammed observatoin
    y = xb + xbg + np.random.normal(0., An, xbg.shape) # each time you receive, we assume i.i.d. AWGN
    
    return y,t

def cwplot(rx,t,fs:int) -> None:
#%% time 
    fg = figure(1); fg.clf()
    ax = fg.gca()
    ax.plot(t,rx)
    ax.set_xlabel('time [sec]')
    ax.set_ylabel('amplitude')
    ax.set_title('Noisy, jammed receive signal')
#%% periodogram
    if DTPG >= (t[1]-t[0]):
        dt = (t[1]-t[0])/2
    else:
        dt = DTPG

    dtw = 2*dt #  seconds to window
    tstep = ceil(dt*fs)
    wind = ceil(dtw*fs);
    Nfft = zeropadfactor*wind
 
    fg = figure(3); fg.clf()
    ax = fg.gca()

    f,Sraw = welch(rx,fs,nperseg=wind,noverlap=tstep,nfft=Nfft);
    ax.plot(f,Sraw,'r',label='raw signal')

    ax.set_yscale('log')
    ax.set_xlim([1400,1600])
    ax.set_xlabel('frequency [Hz]')
    ax.set_ylabel('amplitude')
    ax.legend()
    
def cw_est(rx, fs:int, method:str='esprit'):
    """
    estimate beat freuqency using subspace frequency estimation techniques.
    This is much faster in Fortran, but to start using Python alone doesn't require compiling Fortran.
    
    ESPRIT and RootMUSIC are two popular subspace techniques.
    
    Matlab's rootmusic is a far inferior FFT-based method with very poor accuracy vs. my implementation.
    """
    assert isinstance(method,str)
    method = method.lower()
    
    if method == 'esprit':
#%% ESPRIT
        #fbhat,conf = Sr.subspace.esprit(y,1,10,fs) # FORTRAN
        fb_est,conf = esprit(rx,4,1000,fs)
#%% ROOTMSUIC
    elif method == 'rootmusic':
        fb_est,conf = rootmusic(rx,4,1000,fs)
    else:
        raise ValueError(f'unknown estimation method: {method}')
        
    return fb_est,conf
    
def cwload(fn,fs:int,tlim):
    """
    Often we load data from GNU Radio in complex64 (what Matlab calls float32) format. 
    there are other choices too.
    complex64 means single-precision complex floating-point data I + jQ.
    """
    assert len(tlim) == 2,'specify start and end times'
    
    si = (int(tlim[0]*fs), int(tlim[1]*fs))
    
    i = slice(si[0],si[1])
    print(f'using samples: {si[0]} to {si[1]}')
    
    rx = np.fromfile(fn,'complex64')[i]
    
    t1 = rx.size/fs # end time [sec]
    
    t = np.arange(0, t1, 1/fs)
    
    return rx,t


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='data file .bin to analyze',nargs='?',default=None)
    p.add_argument('-fs',help='baseband sampling frequency [Hz]',type=float,default=20e3)
    p.add_argument('-t','--tlim',help='time to analyze e.g. -t 3 4 means process from t=3  to t=4 seconds',nargs=2,type=float )
    p = p.parse_args()
    
    if p.fn is None: #simulation
        rx,t = cwsim(p.fs)
    else: # load data file
        rx,t = cwload(p.fn,p.fs,p.tlim)
#%% estimate beat frequency
    fb_est,conf = cw_est(rx,p.fs)
    print('estimated beat frequencies',fb_est)
    print('confidence',conf)
#%% plot
    cwplot(rx,t,p.fs)


    
    show()
