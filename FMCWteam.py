from pathlib import Path
import scipy.signal as signal
from signal_subspace import esprit
import numpy as np
from matplotlib.pyplot import figure,show

bytesperelement=8  # complex64
Nplot=20000

def load_bin(fn,start,end):
  """
  GNU Radio marshalls complex64 data in pairs, as read by np.fromfile()
  """
  with fn.open('rb') as f:
      f.seek(start*bytesperelement)
      rx_array = np.fromfile(f,'complex64',end-start)

  if 1:
      ax = figure().gca()
      ax.plot(range(start,start+Nplot), rx_array[:Nplot])
      ax.set_xlabel('{} sample index'.format(fn.name))
      ax.set_title('{}\n{}'.format(fn.name,rx_array.dtype))
      show()

  print ('rx .bin file: ', fn)

  return rx_array

def get_peaks(rx):
  peaks = signal.argrelmax(rx, order=10000)[0]

  peak_diffs = np.diff(peaks)

  if np.isfinite(peak_diffs):
      print('avg peak distance:', peak_diffs.mean())
      print('max peak distance:', peak_diffs.max())
      print('min peak distance:', peak_diffs.min())

      L = peak_diffs.min()
  else:
      L= None

  return peaks, L


def main(fn,start,end):
  fn = Path(fn).expanduser()
  #rx_array is loading the last 45% of the waveform from the file
  rx_array = load_bin(fn, start, end)
  #peak_array holds the indexes of each peak in the waveform
  #peak_distance is the smallest distance between each peak
  peak_array,peak_distance = get_peaks(rx_array)
  l = peak_distance-1
  print('using window: ',l,'\n')
  #remove first peak
  peak_array= peak_array[1:]
  Npulse=len(peak_array)-1
  print(Npulse,'pulses detected')
  wind = signal.hanning(l)
  Ntone = 2
  Nblockest = 160
  fs = 4e6  # [Hz]
  data = np.empty([Npulse,l])
  #set each row of data to window * (first l samples after each peak)
  for i in range(Npulse):
    data[i,:] = wind * rx_array[peak_array[i]:peak_array[i]+l]

  fb_est, sigma = esprit(data, Ntone, Nblockest, fs)
  print ('fb_est',fb_est)
  print ('sigma: ', sigma)
  drange = (3e8*fb_est) /  (2e6/.1)
  print ('range: ',drange,'\n')



if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='radar .bin file to load')
    p.add_argument('start',help='start sample to read',nargs='?',type=int,default=60000)
    p.add_argument('end',help='start sample to read',nargs='?',type=int,default=90000)
    p = p.parse_args()

    main(p.fn,p.start,p.end)
