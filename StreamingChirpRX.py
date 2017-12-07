#!/usr/bin/env python
"""Streaming processing of received radar data, from Virginia Tech pulsed transmitter
Start by chunking into N PRI chunks.
For now, choose to upsample RX to TX.

./StreamingChirpRX.py ~/data/eclipse/zenodo/radar2017-08-22T00-52-40_3.62MHz.bin 192e3 -t0 1800 -o /tmp/test.h5

./StreamingChirpRX.py sim
"""
import sys
from pathlib import Path
import fractions
import numpy as np
import h5py
import scipy.signal
from matplotlib.pyplot import draw,pause
#
from radioutils import loadbin
from piradar.plots import plotxcor,plotraw
#
LSAMP = 8  # 8 bytes per single precision complex64
Nsim = 10000 # number of simulated pulses

def analyze(P:dict):

    tx = loadbin(P['txfn'], P['txfs'], tlim=(0,P['tm']))
    if P['verbose']:
        plotraw(tx, None, P['txfs'])
    print(f'Using {P["pri"]*1000} ms PRI for {P["tm"]*1e6} us chirp, with {P["Nchirp"]} pulses incoherently integrated')
# %%
    NrxPRI = int(P['pri']*rxfs)  # samples in a PRI
    Lrx = NrxPRI*P['Nchirp']

    if P['rxfn'] is not None:
        Nsampfile = P['rxfn'].stat().st_size//LSAMP
        Tfile = Nsampfile / P['rxfs']
        print(P['rxfn'], f'is {Tfile:0.1f} seconds long')
        isamp = range(0, Nsampfile, Lrx)

    else:
        print('simulation')
        isamp = range(0, Nsim*Lrx, Lrx)

    t = np.array(isamp) / P['txfs']  # elapsed time seconds
    if P['t0'] is not None:
        t += P['t0']
# %%
    if P['outfn']:
        print('writing',outfn)
        with h5py.File(outfn,'w') as f:
            f.create_dataset('Rxy',shape=(t.size, int(NrxPRI*P['resample'])),
                             dtype=np.complex128,chunks=True,compression='gzip')
            f['t'] = t
            f['lags'] = np.arange(-NrxPRI//2,NrxPRI//2)
            f['t0'] = P['t0']
            f['cmd'] = ' '.join(sys.argv)
            f['fs'] = P['txfs']


    for k,(i,j) in enumerate(zip(isamp,isamp[1:])):
        if P['rxfn'] is None:
            rx = 0.05*tx + 0.1*tx.max()*(np.random.randn(P['Nchirp'],tx.size)
                                         + 1j*np.random.randn(P['Nchirp'],tx.size))
            rx = rx.ravel()
        else:
            rx = loadbin(P['rxfn'], P['rxfs'], tlim=P['t0'], isamp=(i, j))

        lags = procchunk(rx, tx, P)

        if outfn:
            with h5py.File(outfn,'a') as f:
                f['Rxy'][k,:] = lags

        print(f'processing t={t[k]:.2f} sec., {t[k]/Tfile*100:.3f} % complete.\r',end="")


def procchunk(rx, tx, P:dict):
    if P['rxfn'] is not None:
        rx = scipy.signal.resample_poly(rx,
                                        P['resample'].numerator,
                                        P['resample'].denominator)

    fs = P['txfs']
# %% resamples parameters
    NrxPRI = int(fs * P['pri']) # Number of RX samples per PRI (resampled)
    assert NrxPRI >= tx.size,'PRI must be longer than chirp length!'

    NrxChirp = rx.size // NrxPRI # number of complete PRIs received in this data
    assert NrxChirp == P['Nchirp']

    Rxy = 0.
    for i in range(P['Nchirp']):
        r = rx[i*NrxPRI:(i+1)*NrxPRI]
        Rxy += np.correlate(tx, r,'same')

    if P['verbose']:
        plotxcor(Rxy, fs)
        draw()
        pause(0.1)

    return Rxy


def loadplot(P:dict):
    """load already processed correlation data and plot"""
    with h5py.File(P['rxfn'], 'r') as f:
        fs = f['fs'].value
        t = f['t'][:]
        lags = f['lags'][:]
        t0 = f['t0'].value
        Rxy = f['Rxy']  # too big for RAM




if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('rxfn',help='receive data filename')
    p.add_argument('rxfs',help='receiver sample freq.',nargs='?',type=float)
    p.add_argument('-txfn',help='transmit chirp sample',default='~/data/eclipse/txchirp.bin')
    p.add_argument('-txfs',help='transmit sample freq.',type=float, default=2e6)
    p.add_argument('-pri',help='pulse repetition interval [sec]',type=float, default=3.75e-3)
    p.add_argument('-N','--Nchirp',help='number of chirps to chunk',type=int, default=1000)
    p.add_argument('-tm',help='chirp length [seconds]',type=float,default=250e-6)
    p.add_argument('-v','--verbose',action='store_true')
    p.add_argument('-o','--outfn',help='output for Rxy')
    p.add_argument('-t0',help='skip ahead to start at this elapsed time',type=float)
    p = p.parse_args()

# %% setup analysis type
    outfn = Path(p.outfn).expanduser() if p.outfn else None

    if p.rxfn == 'sim':
        rxfn = None
        rxfs = p.txfs
    else:
        rxfn = Path(p.rxfn).expanduser()
        rxfs = p.rxfs

    P = {'rxfn':rxfn,
         'rxfs':rxfs,
         'txfn':Path(p.txfn).expanduser(),
         'txfs':p.txfs,
         'pri':p.pri,
         'Nchirp':p.Nchirp,
         'tm':p.tm,
         't0':p.t0,
         'outfn':outfn,
         'verbose':p.verbose,
         }

    if p.txfs and p.rxfs:
        P['resample'] = fractions.Fraction(p.txfs/p.rxfs).limit_denominator()

    if P['rxfn'].suffix == '.bin':
        analyze(P)
    elif P['rxfn'].suffix == '.h5':
        loadplot(P)