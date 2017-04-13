#!/usr/bin/env python
"""
Simply plots average power spectrum of a GNU Radio received file.
Must know what sample rate of file was.

CW Example
./PlotSpectrum.py ~/Dropbox/piradar/data/MH_exercise.bin 100e3 -t 2 3 -flim 9950 10050

FMCW Example
./PlotSpectrum.py ~/Dropbox/piradar/data/B200_5GHz_FMCW.bin 10e6 -t 1 1.1
"""
from pathlib import Path
from numpy import fromfile
from matplotlib.pyplot import show,figure
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
        count = -1 # count=None is not accepted

    with fn.open('rb') as f:
        f.seek(startbyte)
        dat = fromfile(f,'complex64',count)

    if dat.size==0:
        raise ValueError(f'read past end of file {fn}, did you specify incorrect time limits?')

    return dat


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='.bin file to process')
    p.add_argument('fs',help='sample rate of .bin file [Hz]',type=float) #float to allow 100e3
    p.add_argument('-t','--tlim',help='start stop [seconds] to load',type=float,nargs=2,default=(0,None))
    p.add_argument('-flim',help='min max frequency [Hz] to plot',nargs=2,type=float)
    p.add_argument('-vlim',help='min max amplitude [dB] to plot',nargs=2,type=float)
    p = p.parse_args()

    fn=Path(p.fn).expanduser()

    fs = int(p.fs) # to allow 100e3 on command line

    dat = loadbin(fn, fs, p.tlim)


#%%
    ax = figure().gca()
    ax.plot(dat.real[:100000])
    ax.set_title('first 100000 points')
    ax.set_xlabel('sample #')
    ax.set_ylabel('amplitude')


    spec(dat.real, fs, p.flim, vlim=p.vlim)
    show()
