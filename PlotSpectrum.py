#!/usr/bin/env python
"""
Plot time & frequency spectrum of a GNU Radio received file.
Also attempts to playback sound from file (optionally, write .wav file)

CW Example (file with Fs=100kHz, Fc=10kHz, taking 4 sec. time steps from 30 to 60 sec., 10x zero-padding)
./PlotSpectrum.py ~/Dropbox/piradar/data/MH_exercise.bin 100e3 -9700 30 60 4 -z 10 -flim 298 302


FMCW Example
./PlotSpectrum.py ~/Dropbox/piradar/data/B200_5GHz_FMCW.bin 10e6 0 10 1

Reference:
http://www.trondeau.com/examples/2010/9/12/basic-filtering.html
https://www.csun.edu/~skatz/katzpage/sdr_project/sdr/grc_tutorial4.pdf
http://www.ece.uvic.ca/~elec350/grc_doc/ar01s12s08.html
"""
from pathlib import Path
import numpy as np
from matplotlib.pyplot import show,figure,subplots
#
from piradar import loadbin,playaudio
from piradar.plots import spec
"""
important parameters:
-----------------
fsaudio: the rate you downsample the signal to. Has to keep all desired radar signals within first Nyquist zone.
binedge "be": chosen on the basis of Radar frequency (e.g. 47 MHz, 2.4 GHz, etc.)
Doppler shift (CW and FMCW) due to relative motion is based on Radar frequency
"""
fsaudio = 8e3 # [Hz] arbitrary sound card  8e3,16e3, etc.
Fc0 = 10e3  # [Hz] carrier frequency before downconversion
be = np.array([0.6, 1, 1.5, 2])  # [Hz]

def cwproc(fn, fsaudio, tlim, fx0, ax=None):
    fn=Path(p.fn).expanduser()

    fs = int(p.fs) # to allow 100e3 on command line
    fsaudio = int(fsaudio)
    decim = int(fs//fsaudio)

    dat,t = loadbin(fn, fs, tlim, fx0, decim)
    if p.fx0 is not None:
        fs //= decim
# %% play sound
    if 0:  # not for when looping, it will try to play dozens of files at once.
        playaudio(dat, fsaudio, p.outwav)
#%% plots
    if 0 and dat.size<500e3: # plots will crash if too many points
        if ax is None:
            ax = figure().gca()
        ax.plot(t + tlim[0], dat.real[:])
        ax.set_title(f'{fn.name} Fs: {fs} Hz  t={tlim[0]}..{tlim[1]}')
        ax.set_xlabel('time [sec]')
        ax.set_ylabel('amplitude')

    f,tt,Sxx,Sp = spec(dat, fs, p.flim, tlim, be, vlim=p.vlim, zpad=p.zeropad)
# %% analysis
    Abin = np.empty(be.size-1)
    for i in range(len(be)-1):
        ibin = (f < be[i+1]) & (f > be[i])
        Abin[i] = Sp[ibin].sum()

    return Abin

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='.bin file to process')
    p.add_argument('fs',help='sample rate of .bin file [Hz]',type=float) #float to allow 100e3
    p.add_argument('fx0',help='downconvert center frequency shift [Hz]',type=float)
    p.add_argument('tlim',help='start stop increment [seconds] to load',type=float,nargs=3,default=(0,100,4))
    p.add_argument('-flim',help='min max frequency [Hz] to plot',nargs=2,type=float)
    p.add_argument('-vlim',help='min max amplitude [dB] to plot',nargs=2,type=float, default=(-100,-30))
    p.add_argument('-z','--zeropad',help='zeropad factor',type=int,default=1)
    p.add_argument('-o','--outwav',help='.wav output filename')
    p = p.parse_args()

    tlim = np.arange(p.tlim[0], p.tlim[1], p.tlim[2])
    Nt = tlim.size-1
    Nb = be.size-1

    be += Fc0 + p.fx0

    Abins = np.empty((Nt, be.size-1))

    for i in range(Nt):
        Abins[i,:] = cwproc(p.fn, fsaudio, tlim[i:i+2], p.fx0)

    ax = figure().gca()
    for i in range(Nb):
        ax.plot(tlim[:-1], Abins[:,i], label=f'{be[i]}..{be[i+1]} Hz')
    ax.set_xlabel('time [sec.]')
    ax.set_ylabel('power [W/Hz]')
    ax.legend()
    ax.grid()

    show()
