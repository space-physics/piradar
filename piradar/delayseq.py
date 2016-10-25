#!/usr/bin/env python
"""
delays signal (non-integer delays) using FFT frequency-dependent phase shift
"""
from numpy.fft import fft,ifftshift,ifft
from numpy import exp,pi,arange,zeros_like,isreal

def delayseq(x,delay_sec,fs):
    """
    x: input 1-D signal
    delay_sec: amount to shift signal [seconds]
    fs: sampling frequency [Hz]

    xs: time-shifted signal
    """

    assert x.ndim == 1, 'only 1-D signals for now'

    delay_samples = delay_sec*fs
    delay_int = round(delay_samples)

    nfft = nextpow2(x.size+delay_int)

    fbins = 2*pi*ifftshift((arange(nfft)-nfft//2))/nfft

    X = fft(x,nfft)
    Xs = ifft(X*exp(-1j*delay_samples*fbins))

    if isreal(x[0]):
        Xs = Xs.real

    xs = zeros_like(x)
    xs[delay_int:] = Xs[delay_int:x.size]

    return xs


def nextpow2(n):
    return 2**(n-1).bit_length()
