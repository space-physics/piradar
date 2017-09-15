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
from matplotlib.pyplot import show
#
from radioutils import am_demod, ssb_demod,loadbin, playaudio
from piradar import plotraw, spec

fsaudio = 48e3 # [Hz]


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
    p.add_argument('-fx',help='downconversion frequency [Hz] (default no conversion)',type=float)
    p.add_argument('-plotmin',help='lower limit of spectrum display',type=float,default=-135)
    p.add_argument('-audiobw',help='desired audio bandwidth [Hz] for demodulated',type=float)
    p.add_argument('-frumble',help='HPF rumble filter [Hz]',type=float)
    p.add_argument('-wav',help='write wav file of AM demodulated audio')
    p.add_argument('-demod',help='am ssb')
    p.add_argument('-fc',help='carrier injection frequency (baseband) [Hz]',type=float,default=0.)
    p = p.parse_args()

    fs = p.rxfs

    rx = loadbin(p.fn, fs, p.tlim)
# %% RF plots
    plotraw(rx, None, fs)
    spec(rx, fs, zpad=p.zeropad)
# %% demodulation (optional)
    aud = None
    if p.demod=='chirp':
        tx = loadbin(p.txfn, p.txfs)
        if tx is None:
            raise RuntimeError('You must specify receieve AND transmit files for chirp processing')
        aud = rx * tx.conjugate()
    elif p.demod=='am':
        aud = am_demod(p.amplitude*rx, fs, fsaudio, p.fc, p.audiobw, frumble=p.frumble, verbose=True)
    elif p.demod=='ssb':
        aud = ssb_demod(p.amplitude*rx, fs, fsaudio, p.fc, p.audiobw,verbose=True)
# %% baseband plots
    if 1:
        plotraw(aud,None,fsaudio)
        spec(aud, fsaudio)
# %% final output
    playaudio(aud, fsaudio, p.wav)

    show()