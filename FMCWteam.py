from pathlib import Path
import scipy
import scipy.signal as signal
from signal_subspace import esprit
import numpy as np
from matplotlib.pyplot import figure,show

bytesperelement=8  # complex64

def load_bin(fn,start,end):
  #return the percentage 'start' of the array starting from end
  with fn.open('rb') as f:
      f.seek(start*bytesperelement)
      rx_array = np.fromfile(f,'complex64',end-start)

  if 1:
      ax = figure().gca()
      ax.plot(range(start,end),rx_array)
      ax.set_xlabel('{} sample index'.format(fn.name))
      ax.set_title('{}\n{}'.format(fn.name,rx_array.dtype))
      show()

  print ('rx .bin file: ', fn)
  print ('rx_array: ', rx_array)
  print ('len: ',len(rx_array),'\n')
  return rx_array

def get_peaks(rx_array,a_len):
  i=0
  old_peak=0
  current_peak=0
  peak_diffs =[]
  peaks = []
  while (i<a_len):
    if(rx_array[i]>.072):
      j=i
      current_max=rx_array[i];
      max_index= i
      for j in range(i, i+10000):
        if (rx_array[j]>current_max):
          max_index=j
          current_max=rx_array[j]
      old_peak=current_peak
      current_peak=max_index
      peaks.append(max_index)
      peak_diffs.append(current_peak-old_peak)
      print (max_index, current_max)
      i=i+10000
    i=i+1
  print('avg peak distance: ', np.mean(peak_diffs))
  print('max peak distance: ', np.max(peak_diffs))
  print('min peak distance: ', np.min(peak_diffs),'\n')
  return peaks,np.min(peak_diffs)


def main(fn,start,end):
  fn = Path(fn).expanduser()
  #rx_array is loading the last 45% of the waveform from the file
  rx_array = load_bin(fn, start, end)
  #peak_array holds the indexes of each peak in the waveform
  #peak_distance is the smallest distance between each peak
  peak_array,peak_distance = get_peaks(rx_array, len(rx_array))
  l= peak_distance-1
  print('using window: ',l,'\n')
  #remove first peak
  peak_array= peak_array[1:]
  Npulse=len(peak_array)-1
  wind = signal.hanning(l)
  Ntone = 2
  Nblockest = 160
  fs = 4*(10**6)
  data = np.empty([Npulse,l])
  #set each row of data to window * (first l samples after each peak)
  for i in range(Npulse):
    data[i,:] = wind * rx_array[peak_array[i]:(peak_array[i]+l)]

  print('data:\n ',data,'\n')
  fb_est,conf = esprit(data,Ntone,Nblockest,fs)
  print ('fb_est',fb_est,'\n')
  print ('conf: ',conf,'\n')
  drange = (3*(10**8)*fb_est)/(2*(10**6)/.1)
  print ('range: ',drange,'\n')



if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='radar .bin file to load')
    p.add_argument('start',help='start sample to read',nargs='?',type=int,default=52000)
    p.add_argument('end',help='start sample to read',nargs='?',type=int,default=52100)
    p = p.parse_args()

    main(p.fn,p.start,p.end)
