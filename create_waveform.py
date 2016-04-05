#!/usr/bin/env python3
#
# Create waveform files for hfradar
# Juha Vierinen
from numpy import empty,zeros, array,arange,exp,complex64,pi
from numpy.fft import ifft,fft
from numpy.random import seed,random
import scipy.signal
from io import BytesIO
import subprocess
try:
    import stuffr
    from matplotlib.pyplot import show
except ImportError:
    show=None


# seed is a way of reproducing the random code without
# having to store all actual codes. the seed can then
# act as a sort of station_id.
def create_pseudo_random_code(clen=10000,rseed=0):
    seed(rseed)
    phases = array(exp(1j*2.0*pi*random(clen)),
                         dtype=complex64)
    if show is not None:
        stuffr.plot_cts(phases[0:100])
        show()

    return phases

# oversample a phase code by a factor of rep
def rep_seq(x,rep=10):
    L = len(x)*rep
    res = empty(L,dtype=x.dtype)
    idx = arange(len(x))*rep
    for i in range(rep):
        res[idx+i] = x

    return res

#
# lets use 0.1 s code cycle and coherence assumption
# our transmit bandwidth is 100 kHz, and with a 10e3 baud code,
# that is 0.1 seconds per cycle as a coherence assumption.
# furthermore, we use a 1 MHz bandwidth, so we oversample by a factor of 10.
#
def waveform_to_file(station=0,clen=10000,oversample=10,filter_output=False,outpath=None):
    a = rep_seq(create_pseudo_random_code(clen=clen,rseed=station),rep=oversample)
    if filter_output == True:
        w = zeros([oversample*clen],dtype=complex64) # yes, zeros for zero-padded
        fl = (int(oversample+(0.1*oversample)))
        w[:fl]= scipy.signal.blackmanharris(fl) # W[fl:] \equiv 0
        aa = ifft(fft(w) * fft(a))
        a = (aa/abs(aa).max()).astype(complex64) #normalized, single prec complex

    if outpath:
        ofn = "code-l%d-b%d-%06d.bin"%(clen,oversample,station)
        print('writing {}'.format(ofn))
        a.tofile(ofn)
<<<<<<< HEAD
    else: # on raspberry pi, sudo does not require reentering password via default /etc/sudoers configuration
        obytes=BytesIO()
        obytes.write(a)
	# - by convention is used for stdin pipe
        P = BytesIO(); P.write(a) #have to do as two steps
        p = subprocess.Popen(['sudo', './rpitx','-i-'],stdin=subprocess.PIPE)
        p.communicate(input=P.getvalue())
=======

    return a

>>>>>>> 174e85923fc103f40262095d4fa2894392277605

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(usage="%prog: [options]")
    p.add_argument("-c", "--codelen", type=int,default=10000, help="Code length (%default)")
    p.add_argument('--filter',help='smooth transmit waveform to limit needless bandwidth',action='store_true')
    p.add_argument('-f','--freqmhz',help='transmit center frequency [MHz]  (default 100.1MHz)',type=float,default=100.1)
    p.add_argument('-o','--outpath',action='store_true',help='write to path instead of stdout')

    p = p.parse_args()

    wvfm = waveform_to_file(clen=p.codelen,outpath=p.outpath,filter_output=p.filter)
    if not p.outpath:
        # on raspberry pi, sudo does not require reentering password via default /etc/sudoers configuration
        P = BytesIO(); P.write(a) #have to do as two steps
        p = subprocess.Popen(['sudo', './rpitx','-i-'],stdin=subprocess.PIPE)
        p.communicate(input=P.getvalue())

