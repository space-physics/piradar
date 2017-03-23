#!/usr/bin/env python
"""
Simply plots average power spectrum of a GNU Radio received file.
Must know what sample rate of file was.
"""
from pathlib import Path
from numpy import fromfile
from matplotlib.pyplot import show
#
from piradar.plots import spec

def loadspec(fn,fs):

    fn = Path(fn).expanduser()

    dat = fromfile(str(fn),'complex64')

    spec(dat.real,fs)
    


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='.bin file to process')
    p.add_argument('fs',help='sample rate of .bin file [Hz]',type=int)
    p = p.parse_args()

    dat = loadspec(p.fn,p.fs)

    show()
