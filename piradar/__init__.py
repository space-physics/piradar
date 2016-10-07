"""
Create waveform files for hfradar
Juha Vierinen
"""
try:
    from pathlib import Path
    Path().expanduser()
except (ImportError,AttributeError):
    from pathlib2 import Path

from numpy import empty,zeros, array,arange,exp,complex64,pi
from numpy.fft import ifft,fft
from numpy.random import seed,random
import scipy.signal
from matplotlib.pyplot import hist,figure,show,subplots,sca
try:
    import stuffr
except ImportError:
    stuffr=None
#
Npt = 200

def create_pseudo_random_code(clen=10000,rseed=0,verbose=False):
    """
    seed is a way of reproducing the random code without having to store all actual codes.
    the seed can then act as a sort of station_id.
    """
    seed(rseed)

    # generate a uniform random phase
    phases = array(exp(1j*2.0*pi*random(clen)),
                         dtype=complex64)

    if stuffr is not None:
        stuffr.plot_cts(phases[:Npt])
        show()

    if verbose:
        fg,ax = subplots(4,1)
        sca(ax[0])
        hist(phases.real)#,50)
        sca(ax[1])
        hist(phases.imag)

        ax[2].plot(abs(phases[:Npt])**2)

        ax[3].scatter(phases[:Npt].real,phases[:Npt].imag)

        #hist(random(clen))

    return phases

def rep_seq(x,rep):
    """
    oversample a phase code by a factor of rep
    """
    L = len(x)*rep
    res = empty(L,dtype=x.dtype)
    idx = arange(len(x))*rep
    for i in range(rep):
        res[idx+i] = x

    return res

def waveform_to_file(station,clen=10000,oversample=10, filt=False, outpath=None,verbose=False):
    """
    lets use 0.1 s code cycle and coherence assumption
    our transmit bandwidth is 100 kHz, and with a clen=10e3 baud code,
    that is 0.1 seconds per cycle as a coherence assumption.
    furthermore, we use a 1 MHz bandwidth, so we oversample by a factor of 10.

    NOTE: this writing method doesn't store any metadata-have to tell rpitx the sample rate
    """

    a = rep_seq(create_pseudo_random_code(clen,station,verbose), rep=oversample)

    if filt == True:
        w = zeros([oversample*clen],dtype=complex64) # yes, zeros for zero-padded
        fl = (int(oversample+(0.1*oversample)))
        w[:fl]= scipy.signal.blackmanharris(fl) # W[fl:] \equiv 0
        aa = ifft(fft(w) * fft(a))
        a = (aa/abs(aa).max()).astype(complex64) #normalized, single prec complex

    if outpath:
        p = Path(outpath).expanduser()
        p.mkdir(parents=True,exist_ok=True)
        ofn = p/"code-l{}-b{}-{:06d}.bin".format(clen,oversample,station)
        print('writing {}'.format(ofn))
        a.tofile(str(ofn))

    return a
