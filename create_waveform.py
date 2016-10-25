#!/usr/bin/env python
from io import BytesIO
import subprocess
from numpy import correlate,pi,exp,arange
from numpy.random import normal
from matplotlib.pyplot import figure,show
try:
    import seaborn as sns
except ImportError:
    pass
#
from piradar import waveform_to_file
from piradar.plots import spec
from piradar.delayseq import delayseq

Nstd = 10 # standard deviation of noise
Ajam = 1. # strength of jammer relative to desired
station_id=0 # "callsign" of radar. Totally uncorrelated with other callsigns
dist_m = 90e3 # note too long delays will just wrap with FFT-based delay. Would have to do integer samples + FFT-shift.
c = 299792458 # [m/s]

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="generate PSK waveforms, and optionally transmit them via raspberry pi")
    p.add_argument("-c", "--codelen", type=int, default=10000, help="Code length ")
    p.add_argument('--filter',help='smooth transmit waveform to limit needless bandwidth',action='store_true')
    p.add_argument('-f','--freqmhz', help='transmit center frequency [MHz]',type=float)
    p.add_argument('--fs',help='sample frequency',type=int,default=100000)
    p.add_argument('-o','--outpath',help='write to path instead of stdout')
    p.add_argument('-v','--verbose',action='store_true')

    p = p.parse_args()

    tx = waveform_to_file(station_id,p.codelen, filt=p.filter, outpath=p.outpath,verbose=p.verbose)

    if p.freqmhz: # on-air transmission
        print('Attempting transmission on {} MHz'.format(p.freqmhz))
        # on raspberry pi, sudo does not require reentering password via default /etc/sudoers configuration
        P = BytesIO()
        P.write(tx) #have to do as two lines of code

        cmd = ['sudo', 'rpitx','-mIQ','-s{}'.format(p.fs),'-i-','-f',str(p.freqmhz*1e3)]
        print(' '.join(cmd))

        p = subprocess.Popen(cmd,stdin=subprocess.PIPE)
        p.communicate(input=P.getvalue())
    else: # simulation only
#%% transmit spectrum
        spec(tx, p.fs)
#%% receive cross-correlate
        awgn = (normal(scale=Nstd, size=tx.size) + 1j*normal(scale=Nstd, size=tx.size))

        jam = Ajam * waveform_to_file(station_id+1, p.codelen, filt=p.filter, outpath=p.outpath,verbose=p.verbose)

        # delay transmit signal and add undesired signals
        tdelay_sec = 2*dist_m / c
        print('refl. height {} km -> delay {:.3e} sec'.format(dist_m/1e3,tdelay_sec))

        rx = delayseq(tx,tdelay_sec,p.fs) + awgn + jam

        # receiver action
        Rxy = correlate(tx, rx, 'full')
        lags = arange(Rxy.size)-Rxy.size//2
        pklag = lags[Rxy.argmax()]

        distest_m = -pklag/p.fs/2*c
        print('estimated one-way distance  {:.1f} km'.format(distest_m/1e3))
#%% plot
        Nraw = 100
        t = arange(tx.size) / p.fs

        ax = figure().gca()
        ax.plot(lags,Rxy.real)
        ax.set_title('cross-correlation of receive waveform with transmit waveform')
        ax.set_ylabel('$R_{xy}$')
        ax.set_xlabel('lags')


        ax = figure().gca()
        ax.plot(t[:Nraw],tx[:Nraw],'b',label='TX')
        ax.plot(t[:Nraw],rx[:Nraw],'r--',label='RX')
        ax.set_title('raw waveform preview')
        ax.set_xlabel('time [sec]')
        ax.legend()

        show()
