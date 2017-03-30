#!/usr/bin/env python
"""
When sinusoid frequency separation is small, you can run out of RAM by zero-padding.
Another, faster technique for this case is subspace methods such as Root-MUSIC and ESPRIT.
Michael Hirsch, Ph.D.

Program operation examples:

If no file input, simulation runs.
./CWsubspace.py

If file input, analysis runs on that file (e.g. from real radar data)
./CWsubspace.py data/myfile.bin -fs 100e3

"""
from time import time
from math import pi,ceil
import numpy as np
from scipy.signal import welch
from matplotlib.pyplot import figure,show
# https://github.com/scivision/spectral_analysis/
try: # requires Fortran compiler
    from spectral_analysis.importfort import fort
    Sc,Sr = fort()
    esprit = Sc.subspace.esprit
    print('using fast FORTRAN ESPRIT')
except ImportError: # use Python, much slower
    print('fallback to slow pure Python ESPRIT')
    from spectral_analysis import esprit
from spectral_analysis import rootmusic # rootmusic not yet implemented in Fortran
# SIMULATION ONLY
# target
fb0 = 2. # Hz  arbitrary "true" Doppler frequency sought.
Ab = 0.1
# transmitter
ft = 1.5e3 # [Hz]
At = 0.5
t1 = 3.  # final time (duration of transmission when t0=0) [seconds]
# Noise
An = 1e-1 # standard deviation of AWGN
# --------FFT ANALYSIS parameters------------
# recall DFT is samples of continuous DTFT
zeropadfactor = 1 #arbitrary, expensive way to increase DFT resolution.
# eventually you'll run out of RAM if you want arbitrarily high precision
DTPG = 0.45  #seconds between time steps to plot (arbitrary)
#------- subspace estimation -------
Ntone = 4
Nblockest = 1000

def cwsim(fs):
    """
    This is a simulation of a noisy narrowband CW measurement (any RF frequency)
    """
#%% signal parameters
    fb = ft + fb0 # [Hz]
    t = np.arange(0, t1-1/fs, 1/fs)
#%% simulated transmitter
    xt = At*np.sin(2*pi*ft*t)
    xbg = xt + np.random.normal(0., An, xt.shape) # we receive the transmitter with noise
    #%% simulated target beat signal (noise free)
    xb = Ab*np.sin(2*pi*fb*t)
    #%% compute noisy, jammed observation
    y = xb + xbg + np.random.normal(0., An, xbg.shape) # each time you receive, we assume i.i.d. AWGN

    return y,t

def cwplot(fb_est,rx,t,fs:int,fn) -> None:
#%% time
    fg = figure(1); fg.clf()
    ax = fg.gca()
    ax.plot(t,rx.real)
    ax.set_xlabel('time [sec]')
    ax.set_ylabel('amplitude')
    ax.set_title('Noisy, jammed receive signal')
    #%% periodogram
    if DTPG >= (t[-1]-t[0]):
        dt = (t[-1]-t[0])/4
    else:
        dt = DTPG

    dtw = 2*dt #  seconds to window
    tstep = ceil(dt*fs)
    wind = ceil(dtw*fs);
    Nfft = zeropadfactor*wind

    fg = figure(3); fg.clf()
    ax = fg.gca()

    f,Sraw = welch(rx,fs,nperseg=wind,noverlap=tstep,nfft=Nfft)

    if np.iscomplex(rx).any():
        f = np.fft.fftshift(f); Sraw = np.fft.fftshift(Sraw)

    ax.plot(f,Sraw,'r',label='raw signal')

    fc_est = f[Sraw.argmax()]

    ax.set_yscale('log')
    ax.set_xlim([fc_est-100,fc_est+100])
    ax.set_xlabel('frequency [Hz]')
    ax.set_ylabel('amplitude')
    ax.legend()

    esttxt=''

    if fn is None: # simulation
        ax.axvline(ft+fb0,color='red',linestyle='--',label='true freq.')
        esttxt += f'true: {ft+fb0} Hz '

    for e in fb_est:
        ax.axvline(e,color='blue',linestyle='--',label='est. freq.')

    esttxt += ' est: ' + str(fb_est) +' Hz'

    ax.set_title(esttxt)

def cw_est(rx, fs:int, method:str='esprit'):
    """
    estimate beat frequency using subspace frequency estimation techniques.
    This is much faster in Fortran, but to start using Python alone doesn't require compiling Fortran.

    ESPRIT and RootMUSIC are two popular subspace techniques.

    Matlab's rootmusic is a far inferior FFT-based method with very poor accuracy vs. my implementation.
    """
    assert isinstance(method,str)
    method = method.lower()

    tic = time()
    if method == 'esprit':
#%% ESPRIT
        fb_est,conf = esprit(rx,Ntone,Nblockest,fs)
#%% ROOTMUSIC
    elif method == 'rootmusic':
        fb_est,conf = rootmusic(rx,Ntone,Nblockest,fs)
    else:
        raise ValueError(f'unknown estimation method: {method}')
    print(f'computed via {method} in {time()-tic} seconds.')
#%% improvised process for CW only without notch filter
    # assumes first two results have largest singular values (from SVD)
    i = fb_est > 0
    fb_est = fb_est[i]; conf = conf[i]

    ii = np.argpartition(conf,Ntone//2-1)[:Ntone//2-1]
    fb_est = fb_est[ii]; conf = conf[ii]

    return fb_est,conf

def cwload(fn,fs:int,tlim):
    """
    Often we load data from GNU Radio in complex64 (what Matlab calls float32) format.
    there are other choices too.
    complex64 means single-precision complex floating-point data I + jQ.
    """
    if tlim is not None:
        assert len(tlim) == 2,'specify start and end times'

        si = (int(tlim[0]*fs), int(tlim[1]*fs))

        i = slice(si[0],si[1])
        print(f'using samples: {si[0]} to {si[1]}')
    else:
        i = None

    rx = np.fromfile(fn,'complex64')[i].squeeze()

    assert rx.ndim==1

    t1 = rx.size/fs # end time [sec]

    t = np.arange(0, t1, 1/fs)

    return rx,t


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='data file .bin to analyze',nargs='?',default=None)
    p.add_argument('-fs',help='baseband sampling frequency [Hz]',type=float,default=20e3)
    p.add_argument('-t','--tlim',help='time to analyze e.g. -t 3 4 means process from t=3  to t=4 seconds',nargs=2,type=float )
    p.add_argument('--noest',help='skip estimation (just plot) for debugging',action='store_true')
    p = p.parse_args()

    if p.fn is None: #simulation
        rx,t = cwsim(p.fs)
    else: # load data file
        rx,t = cwload(p.fn,p.fs,p.tlim)
#%% estimate beat frequency
    if not p.noest:
        fb_est,conf = cw_est(rx,p.fs)
        print('estimated beat frequencies',fb_est)
        print('confidence',conf)
#%% plot
    cwplot(fb_est,rx,t,p.fs,p.fn)

    show()
