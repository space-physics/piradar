#!/usr/bin/env python
"""
Plot time & frequency spectrum of a GNU Radio received file.
Also attempts to playback sound from file (optionally, write .wav file)

CW Example
./PlotSpectrum.py ~/Dropbox/piradar/data/MH_exercise.bin 100e3 -t 26 28 -fx0 -9700 -z 350 -flim 200 400


FMCW Example
./PlotSpectrum.py ~/Dropbox/piradar/data/B200_5GHz_FMCW.bin 10e6 -t 1 1.1

Reference:
http://www.trondeau.com/examples/2010/9/12/basic-filtering.html
https://www.csun.edu/~skatz/katzpage/sdr_project/sdr/grc_tutorial4.pdf
http://www.ece.uvic.ca/~elec350/grc_doc/ar01s12s08.html
"""
from pathlib import Path
from matplotlib.pyplot import show,figure
#
from piradar import loadbin,playaudio
from piradar.plots import spec

fsaudio = 8e3 # [Hz] arbitrary sound card  8e3,16e3, etc.


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='.bin file to process')
    p.add_argument('fs',help='sample rate of .bin file [Hz]',type=float) #float to allow 100e3
    p.add_argument('-t','--tlim',help='start stop [seconds] to load',type=float,nargs=2,default=(0,None))
    p.add_argument('-flim',help='min max frequency [Hz] to plot',nargs=2,type=float)
    p.add_argument('-vlim',help='min max amplitude [dB] to plot',nargs=2,type=float, default=(-100,None))
    p.add_argument('-fx0',help='center frequency (downshift to) [Hz]',type=float)
    p.add_argument('-z','--zeropad',help='zeropad factor',type=int,default=1)
    p.add_argument('-o','--outwav',help='.wav output filename')
    p = p.parse_args()

    fn=Path(p.fn).expanduser()

    fs = int(p.fs) # to allow 100e3 on command line
    fsaudio = int(fsaudio)
    decim = int(fs//fsaudio)

    dat,t = loadbin(fn, fs, p.tlim, p.fx0, decim)
    if p.fx0 is not None:
        fs //= decim
# %% play sound
    playaudio(dat, fsaudio, p.outwav)
#%% plots
    if dat.size<500e3: # plots will crash if too many points
        ax = figure().gca()
        ax.plot(t+p.tlim[0], dat.real[:])
        ax.set_title('{} Fs: {} Hz'.format(fn.name, fs))
        ax.set_xlabel('time [sec]')
        ax.set_ylabel('amplitude')
    else:
        print('skipped time plotting, too many points:',dat.size)

    spec(dat, fs, p.flim, p.tlim, vlim=p.vlim, zpad=p.zeropad)

    show()
