#!/usr/bin/env python
from io import BytesIO
import subprocess
from numpy import correlate
from numpy.random import normal
from matplotlib.pyplot import figure,show
try:
    import seaborn as sns
except ImportError:
    pass
#
from piradar import waveform_to_file
from piradar.plots import spec

Nstd = 10
station_id=0

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

    if p.freqmhz:
        print('Attempting transmission on {} MHz'.format(p.freqmhz))
        # on raspberry pi, sudo does not require reentering password via default /etc/sudoers configuration
        P = BytesIO()
        P.write(tx) #have to do as two steps


        cmd = ['sudo', 'rpitx','-mIQ','-s{}'.format(p.fs),'-i-','-f',str(p.freqmhz*1e3)]
        print(' '.join(cmd))

        p = subprocess.Popen(cmd,stdin=subprocess.PIPE)
        p.communicate(input=P.getvalue())
    else:
#%% transmit spectrum
        spec(tx, p.fs)
#%% receive cross-correlate
        awgn = (normal(scale=Nstd, size=tx.size) + 1j*normal(scale=Nstd, size=tx.size))
        jam = waveform_to_file(station_id+1,p.codelen,  filt=p.filter, outpath=p.outpath,verbose=p.verbose)
        rx = tx + awgn + jam
        Rxx = correlate(tx,rx,'full')

        ax = figure().gca()
        ax.plot(Rxx)

        show()
