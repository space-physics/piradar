#!/usr/bin/env python
"""
When sinusoid frequency separation is small, you can run out of RAM by zero-padding.
Another, faster technique for this case is subspace methods such as Root-MUSIC and ESPRIT.
Michael Hirsch, Ph.D.
-------------------------------
SIMULATION if no file input.

8 pulse FMCW model, PRI 100 ms
 ./CWsubspace.py -Np 8 -T 0.1 --python

CW model, 1 second long
./CWsubspace.py -Np 1 -T 1

--all    # show all tones, even doubtful estimates
--python # force Python instead of Fortran (necessary for FMCW for now)
--------------------------------------------------------------------------
FILE input: analysis runs on that file (e.g. from real radar data)
./CWsubspace.py ~/redPitayaFs1.25MhzBm500kHzTm20msFb0-115kHz_test1.bin -fs 1.25e6 -t 6.975 6.99 -fx0 115e3 --all

./CWsubspace.py ~/redPitayaFs1.25MhzBm500kHzTm20msFb0-115kHz_test1.bin -fs 1.25e6 -t 6.995 7.01 -fx0 115e3 --all

"""
from pathlib import Path
from time import time
from math import pi,ceil
import numpy as np
import scipy.signal as signal
from matplotlib.pyplot import figure,subplots,show
# https://github.com/scivision/signal_subspace/
try: # requires Fortran compiler
    from signal_subspace.importfort import fort
    Sc,Sr = fort()
except ImportError: # use Python, much slower
    print('could not load Fortran ESPRIT')
    pass
from signal_subspace import esprit, rootmusic

# SIMULATION ONLY
# target
fb0 = 40.1  # Hz  arbitrary "true" beat frequency sought.
Ab = 0.1    # target amplitude
# transmitter
ft = 1500  # [Hz]
At = 0.5    # transmitter amplitude ~ Power
# Noise
snr = 50 # [dB]  # assumes unit target amplitude, scale accordingly
# -------- FFT ANALYSIS parameters------------
# recall DFT is samples of continuous DTFT
zeropadfactor = 4 #arbitrary, expensive way to increase DFT resolution.
# eventually you'll run out of RAM if you want arbitrarily high precision
DTPG = 0.05  #seconds between time steps to plot (arbitrary)
#------- subspace estimation -------
Nblockest = 160  # CW ONLY
#----- audio
fsaudio = 48000 # [Hz]

def cwsim(fs,Npulse,tend):
    """
    This is a simulation of a noisy narrowband CW measurement (any RF frequency)
    """
# %% signal parameters
    fb = ft + fb0 # [Hz]
    t = np.arange(0, tend-1/fs, 1/fs)
# %% simulated transmitter
    y = np.empty((Npulse,t.size),order='F',dtype='complex64')
    for i in range(Npulse):
        xt = At*np.exp(1j*2*pi*ft*t + 1j*np.random.uniform(0,2*np.pi))
# %% Noise
        nstd = np.sqrt(10.**(-snr/10.))
        xt += (np.random.normal(0., nstd, xt.shape) +
            1j*np.random.normal(0., nstd, xt.shape))
    #%% simulated target beat signal (noise free)
        xb = Ab*np.exp(1j*2*pi*fb*t + 1j*np.random.uniform(0,2*np.pi))
    #%% compute noisy, jammed observation
    # each time it receives, we assume i.i.d. AWGN
        y[i,:] = xb + xt

    return y.squeeze(), t

def cwplot(fb_est,rx,t,fs:int,fn) -> None:
#%% time
    fg,axs = subplots(1,2,figsize=(12,6))
    ax = axs[0]
    ax.plot(t, rx.T.real)
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

    f,Sraw = signal.welch(rx.ravel(), fs,
                          nperseg=wind,noverlap=tstep,nfft=Nfft,
                          return_onesided=False)

    if np.iscomplex(rx).any():
        f = np.fft.fftshift(f); Sraw = np.fft.fftshift(Sraw)

    ax=axs[1]
    ax.plot(f,Sraw,'r',label='raw signal')

    fc_est = f[Sraw.argmax()]

    #ax.set_yscale('log')
    ax.set_xlim([fc_est-200,fc_est+200])
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

def cw_est(rx, fs:int, Ntone:int, method:str='esprit', usepython=False, useall=False):
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
        if rx.ndim == 2:
            assert usepython,'Fortran not yet configured for multi-pulse case'
            Ntone *= 2


        if usepython or (Sc is None and Sr is None):
            print('Python ESPRIT')
            fb_est, sigma = esprit(rx, Ntone, Nblockest, fs)
        elif np.iscomplex(rx).any():
            print('Fortran complex64 ESPRIT')
            fb_est, sigma = Sc.subspace.esprit(rx,Ntone,Nblockest,fs)
        else: # real signal
            print('Fortran float32 ESPRIT')
            fb_est, sigma = Sr.subspace.esprit(rx,Ntone,Nblockest,fs)

        fb_est = abs(fb_est)
#%% ROOTMUSIC
    elif method == 'rootmusic':
        fb_est, sigma = rootmusic(rx,Ntone,Nblockest,fs)
    else:
        raise ValueError(f'unknown estimation method: {method}')
    print(f'computed via {method} in {time()-tic:.1f} seconds.')
#%% improvised process for CW only without notch filter
    # assumes first two results have largest singular values (from SVD)
    if not useall:
        i = sigma > 0.1 # arbitrary
        fb_est = fb_est[i]
        sigma  = sigma[i]

#        if fb_est.size>1:
#            ii = np.argpartition(sigma, Ntone-1)[:Ntone-1]
#            fb_est = fb_est[ii]
#            sigma = sigma[ii]


    return fb_est, sigma

def cwload(fn:Path, fs:int, tlim, fx0:float=None, D=None):
    """
    Often we load data from GNU Radio in complex64 (what Matlab calls float32) format.
    complex64 means single-precision complex floating-point data I + jQ.

    It is useful to frequency translate and downsample the .bin file to drastically
    conserve RAM and CPU in later steps.
    """
    fn = Path(fn).expanduser()
# %% load (part of) file
    if tlim is not None:
        assert len(tlim) == 2,'specify start and end times'

        si = (int(tlim[0]*fs), int(tlim[1]*fs))

        i = slice(si[0], si[1])
        print(f'using samples: {si[0]} to {si[1]}')
    else:
        i = None

    rx = np.fromfile(str(fn),'complex64')[i].squeeze()
    assert rx.ndim==1
# %% assign elapsed time vector
    t1 = rx.size/fs # end time [sec]
    t = np.arange(0, t1, 1/fs)
# %% frequency translate and downsample
    if fx0 is not None:
        bx = np.exp(1j*2*np.pi*fx0*t)
        rx *= bx[:rx.size] # downshifted

    Ntaps = 199
    D = 26

    rx = signal.decimate(rx, D, Ntaps, 'fir', zero_phase=True)
    t = t[::D]

    return rx, t


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='data file .bin to analyze',nargs='?',default=None)
    p.add_argument('-fs',help='baseband sampling frequency [Hz]',type=float,default=16e3)
    p.add_argument('-Np',help='number of pulses to integrate',type=int,default=1)
    p.add_argument('-fx0',help='frequency translation center frequency',type=float)
    p.add_argument('-Nt',help='number of tones to find',type=int,default=2)
    p.add_argument('-T',help='pulse length (seconds)',type=float,default=0.1)
    p.add_argument('-t','--tlim',help='time to analyze e.g. -t 3 4 means process from t=3  to t=4 seconds',nargs=2,type=float )
    p.add_argument('-m','--method',help='subspace method (esprit,rootmusic)',default='esprit')
    p.add_argument('--noest',help='skip estimation (just plot) for debugging',action='store_true')
    p.add_argument('--python',help='force Python subspace (disable Fortran) for debugging',action='store_true')
    p.add_argument('--all',help='show all tone freq, including feedthrough',action='store_true')
    p = p.parse_args()

    fs = p.fs

    if p.fn is None: #simulation
        rx,t = cwsim(fs, p.Np, p.T)
    else: # load data file
        DecimateFactor = fs//fsaudio
        rx,t = cwload(p.fn, fs, p.tlim, p.fx0,DecimateFactor)
        fs //= DecimateFactor
#%% estimate beat frequency
    if not p.noest:
        fb_est,conf = cw_est(rx, fs, p.Nt, p.method, p.python, p.all)
        print('estimated beat frequencies',fb_est)
        print('sigma',conf)
#%% plot
    cwplot(fb_est,rx.squeeze(),t, fs, p.fn)
    show()
