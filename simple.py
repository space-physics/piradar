#!/usr/bin/env python
"""
Juha Vierinen
a very simple script to create a complex baseband binary phase coded PRN code.
If you guys can transmit and receive this continuously in loopback mode without any glitches,
then using the system for radar is not too far away.
"""

import numpy as np
from matplotlib.pyplot import figure,show,subplots
import h5py
import random

# simple interpolation
def rep(x,rep_len):
    """ interpolate """
    z = np.zeros(len(x)*rep_len,dtype=x.dtype)
    for i in range(len(x)):
        for j in range(rep_len):
            z[i*rep_len+j]=x[i]

    return z

def create_prn(L=1000,seed=0):
    """
    we can send continuously-variable phase modulation or discrete states like BPSK.
    For BPSK, amplitude values of {-1,1} imply 180 degree phase shift at value change.
    """
    np.random.seed(seed)
    # complex sinusoid with uniform random phase
    #sig = np.exp(1j*2.*np.pi*np.random.random(L)).astype('complex64')

    # code (amplitude -1,1 for BPSK)
    code = np.array([random.choice((-1,1)) for i in range(L)],dtype='complex64')
    return code


if __name__ == "__main__":
    seed = 0
    # 1 MHz sample rate, 1000 bit PRN code,
    # 100 bit baud length, seed 0
    code = rep(create_prn(L=1000,seed=seed),100)
    # write code to hdf5 file
    with h5py.File("code-l1000-b100.h5","w") as f:
        f["code"]=code
        f["seed"]=seed

#%% plot
    fg = figure(1); fg.clf()
    ax = fg.gca()
    ax.scatter(code.real,code.imag)
    ax.axhline(0,linestyle='--',color='gray',alpha=0.5)
    ax.axvline(0,linestyle='--',color='gray',alpha=0.5)
    ax.set_title('Constellation diagram')



    figure(2).clf()
    fg,ax = subplots(2,1,sharex=True,sharey=True,num=2)
    ax[0].plot(code.real)
    ax[0].set_title('Real')
    ax[1].plot(code.imag)
    ax[1].set_title('Imag')
    ax[1].set_xlabel("time (us)")

    ax[0].set_ylabel("Complex amplitude")
    fg.suptitle("PRN code")

    show()
