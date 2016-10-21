#!/usr/bin/env python
"""
a very simple script to create a complex baseband binary phase coded PRN code. 
If you guys can transmit and receive this continuously in loopback mode without any glitches, 
then using the system for radar is not too far away. 
"""

#!/usr/bin/env python

import numpy as n
import matplotlib.pyplot as plt
import h5py 
# simple interpolation
def rep(x,rep_len):
    """ interpolate """
    z = n.zeros(len(x)*rep_len,dtype=x.dtype)
    for i in range(len(x)):
        for j in range(rep_len):
            z[i*rep_len+j]=x[i]
    return(z)

def create_prn(len=1000,seed=0):
    # wtf is this so complicated?)
    n.random.seed(seed)
    phases=n.array(n.exp(1.0j*2.0*n.pi*n.random.random(len)),
                   dtype=n.complex64)
    phases=n.angle(phases).astype(n.complex64)
    phases=-1*n.sign(phases)
    phases=n.complex64(phases)
    return(phases)

if __name__ == "__main__":
    # 1 MHz sample rate, 1000 bit PRN code,
    # 100 bit baud length, seed 0
    code=rep(create_prn(len=1000,seed=0),100)
    # write code to hdf5 file
    ho = h5py.File("code-l1000-b100.h5","w")
    ho["code"]=code
    ho["seed"]=0
    ho.close()

    # plot code
    plt.plot(code.real)
    plt.plot(code.imag)
    plt.ylim([-1.2,1.2])
    plt.xlabel("Samples (us)")
    plt.ylabel("Complex amplitude")
    plt.title("PRN code")
    plt.show()
