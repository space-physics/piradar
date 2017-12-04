#!/usr/bin/env python
"""Streaming processing of received radar data, from Virginia Tech pulsed transmitter
Start by chunking into N PRI chunks.
For now, choose to upsample RX to TX.
"""
from pathlib import Path
import numpy as np
import scipy.signal
#
from radioutils import loadbin
#
UP = 125
DOWN = 12
LSAMP = 8  # 8 bytes per single precision complex64


def procchunk(rx, tx, fs:int):
    rx = scipy.signal.resample_poly(rx, UP, DOWN)
    fs = txfs = P['txfs']



if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('rxfn',help='receive data filename')
    p.add_argument('rxfs',help='receiver sample freq.',type=float)
    p.add_argument('-txfn',help='transmit chirp sample',default='~/data/eclipse/txchirp.bin')
    p.add_argument('-txfs',help='transmit sample freq.',type=float,default=2e6)
    p.add_argument('-pri',help='pulse repetition interval [sec]',type=float,default=3.75e-3)
    p.add_argument('-N','--Nchirp',help='number of chirps to chunk',type=int,default=128)
    p = p.parse_args()

    tx = loadbin(p.txfn, p.txfs)

    rxfn = Path(p.rxfn).expanduser()
    Nsampfile = rxfn.stat().st_size//LSAMP
    Tfile = Nsampfile/p.rxfs
    print(rxfn,f'is {Tfile:0.1f} seconds long')

    chunksamp = p.pri*p.txfs  # samples in a chunk

    isamp = range(0,Nsampfile,int(chunksamp))

    for i,j in zip(isamp,isamp[1:]):
        rx = loadbin(rxfn, p.rxfs, isamp=(i, j))