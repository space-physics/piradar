#!/usr/bin/env python
"""
Takes FMCW wave file and attempts to mitigate signal gaps due to ramp reset.
The best is to program the system not have these gaps to start with.
"""
from pathlib import Path
from scipy.io import wavfile
import scipy.signal as signal
import numpy as np
from matplotlib.pyplot import figure,show
import seaborn

fn = '~/out.wav' # converted from raw data by PlaybackFMCW.grc
ofn= '' # gaps removed
FIRSTGAP=1101 # number of samples to discard at beginning
tm = 10 #[Hz] chirp repetition rate (PRF)


#%%
fn = Path(fn).expanduser()
fs,dat = wavfile.read(fn)
dat = dat[:,0] + 1j*dat[:,1]
dat = dat[FIRSTGAP:]

start = 1600
dat = dat[start:]
Lgood = 1319 # number of good samples per PRI
Lpulse = fs//10

Npulse = dat.shape[0]//Lpulse
#%%
wind = signal.hanning(Lgood)

cdat = np.empty((Npulse*Lgood),dtype=dat.dtype)
for i in range(Npulse):
    cdat[i*Lgood:i*Lgood+Lgood] = wind * dat[i*Lpulse:i*Lpulse+Lgood]
#%%
f,Pxx = signal.periodogram(cdat[2*Lgood:],fs,nfft=40*Lgood)
ax = figure().gca()
ax.plot(f,10*np.log10(Pxx),marker='*')
ax.set_xlabel('frequency [Hz]')
ax.set_ylabel('amplitude [dB]')
ax.set_title('Periodogram: FMCW beat freuquencies')
ax.set_ylim((-30,None))
#%%
if ofn:
    ofn = Path(ofn).expanduser()
    print(f'writing {ofn}')
    wavfile.write(ofn,fs,cdat)