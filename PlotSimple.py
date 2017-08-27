#!/usr/bin/env python
"""
basic plotting of radar data
also AM demodulation and audio playback

example data: https://zenodo.org/record/848275

./PlotSimple.py ~/data/eclipse/wwv_rp0_2017-08-22T13-14-52_15.0MHz.bin 192e3 -t 60 75
"""
from pathlib import Path
import numpy as np
import scipy.signal as signal
from matplotlib.pyplot import figure,draw,show
#
from piradar import loadbin, playaudio
from radioutils import am_demod, ssb_demod


fsaudio = 16e3 # [Hz]

def simple(fn,fs, tlim, fx=None):

    fn = Path(fn).expanduser()

    decim = None #int(fs / fsaudio)

    dat,t = loadbin(fn, fs, tlim, fx, decim)

#    if fx is not None:
#        fs //= decim

    return dat,t

def plots(dat,t,fs,zeropad,audiobw,plotmin=None,fn=''):

    Nfft = int(dat.size*zeropad)

    f,Sp = signal.welch(dat, fs,
                        nperseg=Nfft,
                        window = 'hann',
    #                    noverlap=Nol,
                        nfft=Nfft,
                        return_onesided=False
                        )

    ax = figure().gca()

    ax.plot(f/1e3, 10*np.log10(Sp))
    ax.axvline(-audiobw/1e3,linestyle='--',color='red')
    ax.axvline(audiobw/1e3,linestyle='--',color='red')

    ax.set_ylim((plotmin,None))
    ax.grid(True)
    ax.set_xlabel('baseband freq. [kHz]')
    ax.set_ylabel('relative ampl. [dB]')
    ax.set_title(str(fn))


    draw() # so that plots show while audio is playing


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn')
    p.add_argument('fs',type=float)
    p.add_argument('-t','--tlim',type=float,nargs=2,default=(0,None))
    p.add_argument('-z','--zeropad',type=float,default=1)
    p.add_argument('-a','--amplitude',type=float,help='gain factor for demodulated audio. real radios use an AGC.',default=1.)
    p.add_argument('-fx',help='downconversion frequency [Hz] (default no conversion)',type=float)
    p.add_argument('-plotmin',help='lower limit of spectrum display',type=float,default=-135)
    p.add_argument('-audiobw',help='desired audio bandwidth [Hz] for demodulated AM',type=float,default=3.5e3)
    p.add_argument('-wav',help='write wav file of AM demodulated audio')
    p.add_argument('-demod',help='am ssb')
    p.add_argument('-fssb',help='SSB carrier injection frequency (baseband) [Hz]',type=float,default=0.)
    p = p.parse_args()

    fs = int(p.fs)

    dat,t = simple(p.fn, fs, p.tlim, p.fx)

    plots(dat, t, fs, p.zeropad,p.audiobw, p.plotmin, p.fn)

    aud = None
    if p.demod=='am':
        aud = am_demod(p.amplitude*dat, fs, fsaudio, p.audiobw, verbose=True)
    elif p.demod=='ssb':
        aud = ssb_demod(p.amplitude*dat, fs, fsaudio, p.fssb, p.audiobw,verbose=True)[0]

    playaudio(aud, fsaudio, p.wav)

    show()