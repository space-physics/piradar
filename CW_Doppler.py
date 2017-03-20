#!/usr/bin/env python
"""
Computes Doppler frequency output for target assuming an unmodulated CW emission
"""
c=299792458. #[m/s]

from argparse import ArgumentParser
p = ArgumentParser()
p.add_argument('v',help='target velocity [meters/sec]',type=float)
p.add_argument('ft',help='radar transmit frequency [Hz]',type=float)
p = p.parse_args()

fr = 2*p.v*p.ft/(c-p.v)

print(f'beat frequency {fr:0.1f} Hz')
