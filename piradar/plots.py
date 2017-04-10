from datetime import datetime,timedelta
import numpy as np
from xarray import DataArray
import scipy.signal as signal
from matplotlib.pyplot import figure,subplots
#
from .fwdmodel import plasmaprop
#
DTPG = 0.1
zeropadfactor=1

def spec(sig,Fs:int,flim=None,t0:datetime=None,ftick=None,vlim=None):
    """
    sig: signal to analyze, Numpy ndarray
    """
    twin = 0.200 # time length of windows [sec.]
    Nfft = int(Fs*twin)
    Nol = int(Fs*twin/2)

    f,t,Sxx = signal.spectrogram(sig,fs=Fs,
                                 nfft=Nfft,
                                 nperseg=Nfft,
                                 noverlap=Nol) # [V**2/Hz]
    if t0:
        t = [t0 + timedelta(seconds=T) for T in t]

    f = np.fft.fftshift(f)
    Snorm = np.fft.fftshift(Sxx/Sxx.max(),axes=0) + 1e-10
#%%
    fg,axs = subplots(2,1)
    ttxt = f'$f_s$={Fs} Hz  Nfft {Nfft}  '
    if t0:
        ttxt += datetime.strftime(t0,'%Y-%m-%d')
    fg.suptitle(ttxt, y=0.99)

    if vlim is None:
        vlim = (-100,None)

    ax = axs[0]
    h=ax.pcolormesh(t, f, 10*np.log10(Snorm), vmin=vlim[0])
    fg.colorbar(h,ax=ax).set_label('PSD (dB)')
    ax.set_ylabel('frequency [Hz]')
    ax.set_xlabel('time')
    ax.set_title('Spectrogram')
    ax.autoscale(True,'both',tight=True)
    if flim:
        ax.set_ylim(flim)
    if ftick is not None:
        for ft in ftick:
            ax.axhline(ft,color='red',linestyle='--')
#%%
    ax=axs[1]

    #dtw = 2*DTPG #  seconds to window
    #tstep = np.ceil(DTPG*Fs)
    #wind = np.ceil(dtw*Fs);
    #Nfft = zeropadfactor*wind

    f,Sp = signal.welch(sig,Fs,
                        nperseg=Nfft,
    #                    noverlap=Nol,
    #                    nfft=Nfft,
                        )
    if t0:
        ts = (datetime.strftime(t[0],'%H:%M:%S'),datetime.strftime(t[-1],'%H:%M:%S'))
    else:
        ts = (t[0],t[1])
    ttxt = f'time-averaged spectrum {ts[0]}..{ts[1]}'

    ax.plot(f,10*np.log10(Sp))
    ax.set_ylabel('PSD (dB)')
    ax.set_xlabel('frequency [Hz]')
    ax.set_ylim(vlim)
    ax.set_title(ttxt)
    ax.autoscale(True,'x',True)
    if flim:
        ax.set_xlim(flim)
    if ftick is not None:
        for ft in ftick:
            ax.axvline(ft,color='red',linestyle='--')


    fg.tight_layout()

    return f,t,Sxx

def constellation_diagram(sig):
    ax = figure().gca()
    ax.scatter(sig.real, sig.imag)
    ax.axhline(0, linestyle='--',color='gray',alpha=0.5)
    ax.axvline(0, linestyle='--',color='gray',alpha=0.5)
    ax.set_title('Constellation Diagram')


def raw(tx, rx, fs, Nraw):
    t = np.arange(tx.size) / fs

    ax = figure().gca()
    ax.plot(t[:Nraw],tx[:Nraw].real,'b',label='TX')
    ax.plot(t[:Nraw],rx[:Nraw].real,'r--',label='RX')
    ax.set_title('raw waveform preview')
    ax.set_xlabel('time [sec]')
    ax.legend()

#%% forward model
def summary(iono:DataArray,reflectionheight,f0,latlon,dtime):
    assert isinstance(iono,DataArray)

    ax = figure().gca()
    ax.plot(iono.loc[:,'ne'],iono.alt_km,'b',label='$N_e$')

    if reflectionheight is not None:
        ax.axhline(reflectionheight,color='m',linestyle='--',label='reflection height')

    ax.legend()
    ax.set_ylabel('altitude [km]')
    ax.set_xlabel('Number Density')

    ax.autoscale(True,'y',True)
    ax.set_title(f'({latlon[0]}, {latlon[1]})  {dtime}  @ {f0/1e6:.1f} MHz',y=1.06)

def sweep(iono,fs,B0,latlon,dtime):
    hr = np.zeros(fs.size)
    for i,f in enumerate(fs):
        wp,wH,hr[i] = plasmaprop(iono,f,B0)

    ax = figure().gca()
    ax.plot(fs/1e6, hr)
    ax.set_xlabel('frequency [MHz]')
    ax.set_ylabel('altitude [km]')
    ax.set_title('Reflection Height: first order approx. $\omega_p = \omega$')

def plotR(R,zkm):
    ax = figure().gca()
    if R is not None:
        ax2 = ax.twiny()
        #ax2.plot(dNe,zkm,'r',label='$ \partial N_e/\partial z $')

        ax2.plot(R,zkm,'r',label='$\Gamma$')

        ax2.legend(loc='right')
