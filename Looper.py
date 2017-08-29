#!/usr/bin/env python
"""
Iterates over file in blocks, for FFT processing and/or cross-correlation

example data: https://zenodo.org/record/848275

./PlotLoop.py ~/data/eclipse/wwv_rp0_2017-08-22T13-14-52_15.0MHz.bin 192e3
"""
from pathlib import Path
import numpy as np
from matplotlib.pyplot import figure,draw,pause,show
#
from piradar.delayseq import nextpow2

fsaudio = 48e3 # [Hz]
Lbyte = 8  # complex64 is 8 bytes per sample
wintype = np.hanning

def mainloop(fn,fs, tlim):

    fn = Path(fn).expanduser()

    blocksize = nextpow2(1*fs) # arbitrary, bigger->more gain
    win = wintype(blocksize)
    nfft = blocksize
    f = np.arange(0., fs/2., fs/nfft) # shifted fft freq. bins
# %% setup plot
    ax = figure().gca()
    ax.set_xlabel('frequency [Hz]')
    ax.set_ylabel('PSD [dB/Hz]')
    ht = ax.set_title(fn)
    hp, = ax.plot(f,0*f)
# %% loop
    with fn.open('rb') as f:
        i = 0
        while f:
            block = np.fromfile(f, np.complex64, blocksize)

            X = np.fft.fft(win * block, nfft, axis=-1)
            X = X[:nfft//2]

            Pxx = 1./(fs*nfft) * abs(X)**2
            Pxx[1:-1] = 2*Pxx[1:-1] #scales DC appropriately
# %% live updating plot
            hp.set_ydata(Pxx)
            ht.set_text(f'{fn.stem}: t= {i*blocksize/fs} sec.')
            i += 1


    draw(); pause(0.01) # so that plots show while audio is playing


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn', help='giant .bin file to process SDR radar from')
    p.add_argument('fs', help='sampling frequency [Hz]', type=float)
    p.add_argument('-t','--tlim',help='time limits to work on (sec)',nargs=2,type=float)
    p = p.parse_args()

    fs = int(p.fs)

    mainloop(p.fn, fs, p.tlim)

    show()