#!/usr/bin/env python
"""
basic plotting of radar data
also AM demodulation and audio playback

example data: https://zenodo.org/record/848275

WWV AM audio:  note there is a low frequency beat, possibly due to DC imbalance and having DC leakage beating with downmixed WWV carrier?
./PlotSimple.py wwv_rp0_2017-08-22T13-14-52_15.0MHz.bin 192e3 -t 60 75 -demod am -audiobw 5e3

Tranmit waveform:
./PlotSimple.py txchirp.bin 2e6
"""
import numpy as np
import scipy.signal
import warnings
from matplotlib.pyplot import show
#
from radioutils import am_demod, ssb_demod,loadbin, playaudio
from piradar import plotraw, spec, plotxcor

fsaudio = 48e3 # [Hz]
UP = 125
DOWN = 12

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='receive data filename')
    p.add_argument('-txfn',help='transmit chirp sample filename')
    p.add_argument('-txfs',help='transmit sample rate [Hz]',type=float)
    p.add_argument('rxfs',help='receive sample rate [Hz]',type=float)
    p.add_argument('-t','--tlim',type=float,nargs=2)
    p.add_argument('-z','--zeropad',type=float,default=1)
    p.add_argument('-a','--amplitude',type=float,help='gain factor for demodulated audio. real radios use an AGC.',default=1.)
    p.add_argument('-plotmin',help='lower limit of spectrum display',type=float,default=-135)
    p.add_argument('-audiobw',help='desired audio bandwidth [Hz] for demodulated',type=float)
    p.add_argument('-frumble',help='HPF rumble filter [Hz]',type=float)
    p.add_argument('-wav',help='write wav file of AM demodulated audio')
    p.add_argument('-demod',help='am ssb')
    p.add_argument('-fc',help='carrier injection frequency (baseband) [Hz]',type=float,default=0.)
    p = p.parse_args()

    fs = p.rxfs

    rx = loadbin(p.fn, fs, p.tlim)

    plotraw(rx, None, fs)
# %% demodulation (optional)
    aud = None
    Rxy = None
    txfs = None
    if p.demod=='chirp':
        tx = loadbin(p.txfn, p.txfs)
        if tx is None:
            warnings.warn('simulated chirp reception')
            tx = rx
            rx = 0.02*rx + 0.1*rx.max()*(np.random.randn(rx.size) + 1j*np.random.randn(rx.size))
            txfs = fs
        else:
            rx = scipy.signal.resample_poly(rx, UP, DOWN)
            txfs = fs = p.txfs


        Rxy = np.correlate(tx,rx,'full')
    elif p.demod=='am':
        aud = am_demod(p.amplitude*rx, fs, fsaudio, p.fc, p.audiobw, frumble=p.frumble, verbose=True)
    elif p.demod=='ssb':
        aud = ssb_demod(p.amplitude*rx, fs, fsaudio, p.fc, p.audiobw,verbose=True)
# %% RF plots
    spec(rx, fs, zpad=p.zeropad, ttxt='raw ')
# %% baseband plots
    plotraw(aud,None,fsaudio)
    spec(aud, fsaudio)
# %% chirp plots
    lags = None
    plotxcor(Rxy, txfs)
# %% final output
    playaudio(aud, fsaudio, p.wav)

    show()