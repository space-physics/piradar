#!/usr/bin/env python
"""
Takes FMCW wave file and attempts to mitigate signal gaps due to ramp reset.
The best is to program the system not have these gaps to start with.
"""
from pathlib import Path
from scipy.io import wavfile
import scipy.signal as signal
import numpy as np

fn = '~/out.wav' # converted from raw data by PlaybackFMCW.grc
ofn= '~/out2.wav' # gaps removed
FIRSTGAP=1101 # number of samples to discard at beginning
tm = 10 #[Hz] chirp repetition rate (PRF)


#%%
fn = Path(fn).expanduser()
fs,dat = wavfile.read(fn)
dat = dat[FIRSTGAP:,:]

start = 1600
dat = dat[start:,:]
Lgood = 1319 # number of good samples per PRI
Lpulse = fs//10

Npulse = dat.shape[0]//Lpulse
#%%
wind = signal.hanning(Lgood)

cdat = np.empty((Npulse*Lgood,2),dtype=dat.dtype)
for i in range(Npulse):
    cdat[i*Lgood:i*Lgood+Lgood,:] = wind[:,None] * dat[i*Lpulse:i*Lpulse+Lgood,:]

ofn = Path(ofn).expanduser()
print(f'writing {ofn}')
wavfile.write(ofn,fs,cdat)