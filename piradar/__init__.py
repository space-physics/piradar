"""
Create waveform files for hfradar
Juha Vierinen
"""
from numpy import empty,zeros, array,arange,exp,complex64,pi
from numpy.fft import ifft,fft
from numpy.random import seed,random
import scipy.signal
try:
    import stuffr
    from matplotlib.pyplot import show
except ImportError:
    show=None


def create_pseudo_random_code(clen=10000,rseed=0):
    """
    seed is a way of reproducing the random code without having to store all actual codes.
    the seed can then act as a sort of station_id.
    """
    seed(rseed)
    phases = array(exp(1j*2.0*pi*random(clen)),
                         dtype=complex64)

    if show is not None:
        stuffr.plot_cts(phases[0:100])
        show()

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

def waveform_to_file(station=0,clen=10000,oversample=10,filter_output=False,outpath=None):
    """
    lets use 0.1 s code cycle and coherence assumption
    our transmit bandwidth is 100 kHz, and with a clen=10e3 baud code,
    that is 0.1 seconds per cycle as a coherence assumption.
    furthermore, we use a 1 MHz bandwidth, so we oversample by a factor of 10.

    TODO: this writing method doesn't store any metadata--how will rpitx know the sample rate?
    rpitx makes an assumption of 48kHz I think.
    """

    a = rep_seq(create_pseudo_random_code(clen=clen,rseed=station),rep=oversample)

    if filter_output == True:
        w = zeros([oversample*clen],dtype=complex64) # yes, zeros for zero-padded
        fl = (int(oversample+(0.1*oversample)))
        w[:fl]= scipy.signal.blackmanharris(fl) # W[fl:] \equiv 0
        aa = ifft(fft(w) * fft(a))
        a = (aa/abs(aa).max()).astype(complex64) #normalized, single prec complex

    if outpath:
        ofn = "code-l{}-b{}-{:06d}.bin".format(clen,oversample,station)
        print('writing {}'.format(ofn))
        a.tofile(ofn)

    return a
