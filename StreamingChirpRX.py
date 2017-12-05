#!/usr/bin/env python
"""Streaming processing of received radar data, from Virginia Tech pulsed transmitter
Start by chunking into N PRI chunks.
For now, choose to upsample RX to TX.
"""
from pathlib import Path
import numpy as np
import scipy.signal
from matplotlib.pyplot import draw,pause
#
from radioutils import loadbin
from piradar.plots import plotxcor
#
UP = 125
DOWN = 12
LSAMP = 8  # 8 bytes per single precision complex64


def procchunk(rx, tx, P:dict):
    rx = scipy.signal.resample_poly(rx, UP, DOWN)
    fs = P['txfs']
# %% resamples parameters
    NrxPRI = int(fs * P['pri']) # Number of RX samples per PRI (resampled)
    assert NrxPRI == tx.size

    NrxChirp = rx.size // NrxPRI # number of complete PRIs received in this data
    assert NrxChirp == P['Nchirp']

    Rxy = 0.
    for i in range(P['Nchirp']):
        r = rx[i*NrxPRI:(i+1)*NrxPRI]
        Rxy += np.correlate(tx, r,'same')

    plotxcor(Rxy, fs)
    draw()
    pause(0.5)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('rxfn',help='receive data filename')
    p.add_argument('rxfs',help='receiver sample freq.',type=float)
    p.add_argument('-txfn',help='transmit chirp sample',default='~/data/eclipse/txchirp.bin')
    p.add_argument('-txfs',help='transmit sample freq.',type=float,default=2e6)
    p.add_argument('-pri',help='pulse repetition interval [sec]',type=float,default=3.75e-3)
    p.add_argument('-N','--Nchirp',help='number of chirps to chunk',type=int,default=1000)
    p = p.parse_args()

    P = {'rxfn':Path(p.rxfn).expanduser(),
         'rxfs':p.rxfs,
         'txfn':Path(p.txfn).expanduser(),
         'txfs':p.txfs,
         'pri':p.pri,
         'Nchirp':p.Nchirp,
         }

    tx = loadbin(P['txfn'], P['txfs'], tlim=(0,P['pri']))
    print(f'Using {P["pri"]*1000} ms PRI and {P["Nchirp"]} pulses incoherently integrated')
# %%
    Nsampfile = P['rxfn'].stat().st_size//LSAMP
    Tfile = Nsampfile / P['rxfs']
    print(P['rxfn'], f'is {Tfile:0.1f} seconds long')

    NrxPRI = int(p.pri*p.rxfs)  # samples in a PRI

    isamp = range(0, Nsampfile, NrxPRI*P['Nchirp'])

    for i,j in zip(isamp,isamp[1:]):
        rx = loadbin(P['rxfn'], P['rxfs'], isamp=(i, j))
        procchunk(rx, tx, P)