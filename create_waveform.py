#!/usr/bin/env python
"""
./create_waveform  plot only, don't save or transmit

./create_waveform -o filename  saves psuedorandom phase modulated signal to disk for use with GNU Radio

./create_waveform -qo filename  saves to file WITHOUT plotting

Transmitting on air with -f is a hack for the Raspberry Pi only, we don't use that feature.
"""
from matplotlib.pyplot import show
import seaborn as sns
sns.set_context('talk',font_scale=1.5)
#
from piradar import waveform_to_file,estimate_range,sim_iono
from piradar.plots import spec,raw
#%% simulation parameters
Nstd = 10 # standard deviation of noise
Ajam = 1. # strength of jammer relative to desired
station_id=0 # "callsign" of radar. Totally uncorrelated with other callsigns
dist_m = 10e3 # note too long delays will just wrap with FFT-based delay. Would have to do integer samples + FFT-shift.
c = 299792458 # [m/s]
#%%
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="generate PSK waveforms, and optionally transmit them via raspberry pi")
    p.add_argument("-c", "--codelen", type=int, default=10000, help="Code length ")
    p.add_argument('--filter',help='smooth transmit waveform to limit needless bandwidth',action='store_true')
    p.add_argument('-f','--freqmhz', help='transmit center frequency [MHz]',type=float)
    p.add_argument('--fs',help='sample frequency [Hz]',type=int,default=100000)
    p.add_argument('-o','--outpath',help='write to path instead of stdout')
    p.add_argument('-q','--quiet',help='do not plot anything',action='store_true')
    p.add_argument('-v','--verbose',action='store_true')
    p = p.parse_args()
    
    quiet = p.quiet

    tx = waveform_to_file(station_id,p.codelen, filt=p.filter, outpath=p.outpath,verbose=p.verbose)

    if p.freqmhz: # on-air transmission
        from piradar.raspi import transmit_raspi
        transmit_raspi(tx, p.fs, p.freqmhz)
    else: # simulation only
#%% transmit spectrum
        if not quiet:
            spec(tx, p.fs)
#%% simulate noisy, reflected signal
        rx = sim_iono(tx,p.fs,dist_m,p.codelen,Nstd,Ajam,station_id,p.filter,p.outpath,p.verbose)
#%% receive cross-correlate
        distest_m = estimate_range(tx,rx,p.fs,quiet)
        print('estimated one-way distance  {:.1f} km'.format(distest_m/1e3))
#%% plot
        Nraw = 100 # arbitrary, just for plotting
        if not quiet:
            raw(tx, rx, p.fs, Nraw)

        show()
