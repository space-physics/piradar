#!/usr/bin/env python
"""
Simply plots average power spectrum of a GNU Radio received file.
Must know what sample rate of file was.

Example
~/Dropbox/piradar/data/MH_exercise.bin 100e3 -t 2 3 --flim 9950 10050
"""
from pathlib import Path
from numpy import fromfile
from matplotlib.pyplot import show
#
from piradar.plots import spec

def loadbin(fn:Path,fs:int,tlim):
    """
    we assume PiRadar will always be handling single-precision complex data in/out of FPGA

    We don't load the whole file by default, because it can greatly exceed PC RAM.
    """
    Lbytes = 8  # 8 bytes per single-precision complex

    startbyte = int(Lbytes * tlim[0] * fs)
    if tlim[1] is not None:
        count = int((tlim[1] - tlim[0]) * fs)
    else: # read rest of file from startbyte
        count = None

    with fn.open('rb') as f:
        f.seek(startbyte)
        dat = fromfile(f,'complex64',count)

    return dat


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='.bin file to process')
    p.add_argument('fs',help='sample rate of .bin file [Hz]',type=float) #float to allow 100e3
    p.add_argument('-t','--tlim',help='start stop [seconds] to load',type=float,nargs=2,default=(0,None))
    p.add_argument('--flim',help='min max frequency [Hz] to plot',nargs=2,type=float)
    p = p.parse_args()

    fn=Path(p.fn).expanduser()

    fs = int(p.fs) # to allow 100e3 on command line

    dat = loadbin(fn, fs, p.tlim)


#%%
    spec(dat.real, fs, p.flim)
    show()
