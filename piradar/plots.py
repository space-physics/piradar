from datetime import datetime,timedelta
from numpy import arange,log10
from numpy.fft import fftshift
from scipy.signal import spectrogram
from matplotlib.pyplot import figure,subplots

def spec(sig,Fs:int,flim=None,t0:datetime=None,ftick=None):
    """
    sig: signal to analyze, Numpy ndarray
    """
    twin = 0.200 # time length of windows [sec.]
    Nfft = int(Fs*twin)
    Nol = int(Fs*twin/2)
    
    f,t,Sxx = spectrogram(sig,fs=Fs,
                          nfft=Nfft,
                          nperseg=Nfft,
                          noverlap=Nol) # [V**2/Hz]
    if t0:
        t = [t0 + timedelta(seconds=T) for T in t]

    f = fftshift(f)
    Snorm = fftshift(Sxx/Sxx.max(),axes=0) + 1e-10

    fg,axs = subplots(2,1)
    ttxt = f'$f_s$={Fs} Hz  Nfft {Nfft}  '
    if t0:
        ttxt += datetime.strftime(t0,'%Y-%m-%d')
    fg.suptitle(ttxt, y=0.99)

    ax = axs[0]
    h=ax.pcolormesh(t, f, 10*log10(Snorm),vmin=-40)
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

    Savg = Snorm.mean(axis=1)
    Savg /= Savg.max()
    
    if t0:
        ts = (datetime.strftime(t[0],'%H:%M:%S'),datetime.strftime(t[-1],'%H:%M:%S'))
    else:
        ts = (t[0],t[1])
    ttxt = f'time-averaged spectrum {ts[0]}..{ts[1]}'
    
    ax.plot(f,10*log10(Savg))
    ax.set_ylabel('PSD (dB)')
    ax.set_xlabel('frequency [Hz]')
    ax.set_ylim(-40,None)
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
    t = arange(tx.size) / fs

    ax = figure().gca()
    ax.plot(t[:Nraw],tx[:Nraw].real,'b',label='TX')
    ax.plot(t[:Nraw],rx[:Nraw].real,'r--',label='RX')
    ax.set_title('raw waveform preview')
    ax.set_xlabel('time [sec]')
    ax.legend()