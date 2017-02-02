#!/usr/bin/env python
"""
receive preocessing for waveform
"""
from numpy import complex64,fromfile
#
from piradar import estimate_range

fntx = 'hello/code-l10000-b10-000000.bin'
fnrx = 'hello/rx-sim.bin'
fs = 100000 #a priori from radar transmitter
quiet = False

tx = fromfile(fntx,complex64)
rx = fromfile(fnrx,complex64)

print(tx.size)
print(rx.size)

distest_m = estimate_range(tx,rx,fs,quiet)
print('estimated one-way distance  {:.1f} km'.format(distest_m/1e3))