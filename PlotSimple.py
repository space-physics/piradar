#!/usr/bin/env python
"""
basic plotting of radar data
"""
from pathlib import Path
import numpy as np
import scipy.signal as signal
from piradar import loadbin
from matplotlib.pyplot import figure,show

fsaudio = 8e3 # [Hz]

def simple(fn,fs, tlim, fx=None):
    fn = Path(fn).expanduser()

    decim = int(fs/fsaudio)

    dat,t = loadbin(fn, fs, tlim, fx, decim)

    if fx is not None:
        fs /= decim

    return dat,t

def plots(dat,t,fs,zeropad):

    Nfft = int(dat.size*zeropad)

    f,Sp = signal.welch(dat, fs,
                        nperseg=Nfft,
                        window = 'hann',
    #                    noverlap=Nol,
                        nfft=Nfft,
                        return_onesided=False
                        )

    ax = figure().gca()
    ax.plot(f,10*np.log10(Sp))


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn')
    p.add_argument('fs',type=float)
    p.add_argument('-t','--tlim',type=float,nargs=2,default=(0,None))
    p.add_argument('-z','--zeropad',type=float,default=1)
    p = p.parse_args()

    fs = int(p.fs)

    dat,t = simple(p.fn, fs, p.tlim)

    plots(dat, t, fs, p.zeropad)

    show()