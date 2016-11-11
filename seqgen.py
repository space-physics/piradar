#!/usr/bin/env python
from pathlib import Path
from numpy import arange,fromfile,tile

fn1 = '/tmp/tx0-255.bin'
fn2 = '/tmp/rx0-255.bin'

#%% transmit code write
A = arange(2**8, dtype='uint8')

fn1 = Path(fn1).expanduser()
A.tofile(str(fn1),'')
#%% receive code comparison
B = fromfile(fn2,'uint8',sep='')

match = A==B

#if not match.all():
#    fail = (~match).sum()
#    print('{} bytes mismatch'.format(fail))

