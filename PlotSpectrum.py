#!/usr/bin/env python
"""
Simply plots average power spectrum of a GNU Radio received file.
Must know what sample rate of file was.
"""

from numpy import fromfile
#
from piradar.plots import spec

fn = 'output/out.bin'
fs = 1000000 # [Hz] a priori

dat = fromfile(fn,'complex64')

spec(dat,fs)