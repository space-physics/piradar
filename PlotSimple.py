#!/usr/bin/env python
"""
basic plotting of radar data
also AM demodulation and audio playback

example data: https://zenodo.org/record/848275

WWV AM audio:  note there is a low frequency beat, possibly due to DC imbalance and having DC leakage beating with downmixed WWV carrier?
./PlotSimple.py wwv_rp0_2017-08-22T13-14-52_15.0MHz.bin 192e3 -t 60 75 -demod am -audiobw 5e3

Tranmit waveform:
./PlotSimple.py ~/data/eclipse/txchirp.bin 2e6

Simulate chirp reception in noise:
./PlotSimple.py ~/data/eclipse/txchirp.bin 2e6 -demod chirp

Processing:
./PlotSimple.py ~/data/eclipse/zenodo/radar2017-08-22T00-22-30_5.445MHz.bin 192e3 -t 15000 15002 -txfn ~/data/eclipse/txchirp.bin -txfs 2e6 -demod chirp

./PlotSimple.py ~/data/eclipse/zenodo/radar2017-08-22T00-52-40_3.62MHz.bin 192e3 -t 15002 15004 -txfn ~/data/eclipse/txchirp.bin -txfs 2e6 -demod chirp -pri 3.75e-3

"""
import numpy as np
import scipy.signal
import warnings
from matplotlib.pyplot import show,draw,pause
#
from radioutils import am_demod, ssb_demod,loadbin, playaudio
from piradar.plots import plotraw, spec, plotxcor

fsaudio = 48e3 # [Hz]
UP = 125
DOWN = 12

def getrx(P:dict):
    rx = loadbin(P['rxfn'], P['rxfs'], P['tlim'])
    plotraw(rx, None, P['rxfs'])

    return rx


def dodemod(rx, P:dict):
    if P['demod']=='chirp':
        aud = None
        tx = loadbin(P['txfn'], P['txfs'])
        if tx is None:
            warnings.warn('simulated chirp reception')
            tx = rx
            rx = 0.05*rx + 0.1*rx.max()*(np.random.randn(rx.size) + 1j*np.random.randn(rx.size))
            fs = txfs = P['rxfs']
        else:
            rx = scipy.signal.resample_poly(rx, UP, DOWN)
            fs = txfs = P['txfs']

        txsec = tx.size/txfs # length of TX in seconds
        if P['pri'] is None:
            pri=txsec
        print(f'Using {pri*1000} ms PRI and {P["Npulse"]} pulses incoherently integrated')

# %% integration
        NrxPRI = int(fs * pri) # Number of RX samples per PRI
        NrxStack = rx.size // NrxPRI # number of complete PRIs received in this data
        Nint = NrxStack // P['Npulse'] # Number of steps we'll take iterating
        Nextract = P['Npulse'] * NrxPRI  # total number of samples to extract (in general part of one PRI is discarded after numerous PRIs)

        ax=None
        for i in range(Nint):
            ci = slice(i*Nextract, (i+1)*Nextract)
            rxint = rx[ci].reshape((NrxPRI, P['Npulse'])).mean(axis=1)
            Rxy = np.correlate(tx, rxint, 'full')
            ax = plotxcor(Rxy, txfs, ax)
            draw(); pause(0.5)
    elif P['demod']=='am':
        aud = am_demod(P['again']*rx, fs, fsaudio, P['fc'], p.audiobw, frumble=p.frumble, verbose=True)
    elif P['p.demod']=='ssb':
        aud = ssb_demod(P['again']*rx, fs, fsaudio, P['fc'], p.audiobw,verbose=True)

    return aud

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='receive data filename')
    p.add_argument('-txfn',help='transmit chirp sample filename')
    p.add_argument('-txfs',help='transmit sample rate [Hz]',type=float)
    p.add_argument('rxfs',help='receive sample rate [Hz]',type=float)
    p.add_argument('-pri',help='pulse repetition interval [sec.]',type=float)
    p.add_argument('-Npulse',help='number of pulses to incoherently integrate',type=int,default=1)
    p.add_argument('-tau',help='TX pulse length (sec.) NOT same as PRI in general with < 100% duty cycle.',type=float)
    p.add_argument('-t','--tlim',type=float,nargs=2)
    p.add_argument('-z','--zeropad',type=float,default=1)
    p.add_argument('-a','--amplitude',type=float,help='gain factor for demodulated audio. real radios use an AGC.',default=1.)
    p.add_argument('-plotmin',help='lower limit of spectrum display',type=float,default=-135)
    p.add_argument('-audiobw',help='desired audio bandwidth [Hz] for demodulated',type=float)
    p.add_argument('-frumble',help='HPF rumble filter [Hz]',type=float)
    p.add_argument('-wavfn',help='filename to write wav file of AM demodulated audio')
    p.add_argument('-demod',help='am ssb')
    p.add_argument('-fc',help='carrier injection frequency (baseband) [Hz]',type=float,default=0.)
    p = p.parse_args()

    P = {'rxfn':p.fn,
         'rxfs':int(p.rxfs),
         'txfn':p.txfn,
         'txfs':int(p.txfs),
         'demod':p.demod,
         'pri':p.pri,
         'Npulse':p.Npulse,
         'again':p.amplitude,
         'fc':p.fc,
         'tlim':p.tlim}

# %% load data
    rx = getrx(P)
# %% demodulation (optional)
    aud,fs = dodemod(rx, P)
# %% RF plots
    spec(rx, fs, zpad=p.zeropad, ttxt='raw ')
# %% baseband plots
    plotraw(aud,None,fsaudio)
    spec(aud, fsaudio)
# %% final output
    playaudio(aud, fsaudio, p.wavfn)

    show()
