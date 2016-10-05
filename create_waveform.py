#!/usr/bin/env python
from io import BytesIO
import subprocess
from matplotlib.pyplot import show
import seaborn as sns
#
from piradar import waveform_to_file
from piradar.plots import spec


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="generate PSK waveforms, and optionally transmit them via raspberry pi")
    p.add_argument("-c", "--codelen", type=int, default=10000, help="Code length ")
    p.add_argument('--filter',help='smooth transmit waveform to limit needless bandwidth',action='store_true')
    p.add_argument('-f','--freqmhz', help='transmit center frequency [MHz]',type=float)
    p.add_argument('--fs',help='sample frequency',type=int,default=100000)
    p.add_argument('-o','--outpath',help='write to path instead of stdout')

    p = p.parse_args()

    wvfm = waveform_to_file(clen=p.codelen,outpath=p.outpath,filter_output=p.filter)

    if p.freqmhz:
        print('Attempting transmission on {} MHz'.format(p.freqmhz))
        # on raspberry pi, sudo does not require reentering password via default /etc/sudoers configuration
        P = BytesIO()
        P.write(wvfm) #have to do as two steps


        cmd = ['sudo', 'rpitx','-mIQ','-s{}'.format(p.fs),'-i-','-f',str(p.freqmhz*1e3)]
        print(' '.join(cmd))

        p = subprocess.Popen(cmd,stdin=subprocess.PIPE)
        p.communicate(input=P.getvalue())
    else:
        spec(wvfm,p.fs)
        show()
