% used with GNU Radio  .bin recordings of CW data from 28 March 2017 experiments
% these recordings are after DDC.
% Michael Hirsch, Ph.D.
function PlotCW(fn,fs,varargin)
% PlotCW(fn,fs)
% load the .bin file "fn" recorded from GNU Radio with sample rate "fs" Hz
%
% PlotCW(fn,fs,tstart,tend)
% only load data from .bin file "fn" from time "tstart" to "tend" [seconds]
% this works quickly for large .bin files
%
% Example:
% PlotCW('FMCW_3secnone_7secwave_fs4MHz_Bm1MHz.bin')
 try % for GNU Octave
  pkg load signal
 end

if length(varargin)>=2
    treq = [varargin{1},varargin{2}]; % start, stop times (sec)
    ireq = round(treq*fs);
    count = ireq(2)-ireq(1)+1;
    start = ireq(1);
else
    count=Inf; start=[]; treq=0;
end
%% load data
[~,name,ext] = fileparts(fn);

sig = read_complex_binary(fn, count, start);
Ns = size(sig,2);

t = treq(1):1/fs:Ns/fs-1/fs + treq(1);

radarplot(sig,t,[name,ext],fs)

end

function radarplot(sig,t,name,fs)

%% plot
if 1
  figure(1),clf(1),hold('on')
  
  plot(t,sig,'b','displayname','raw signal')

  xlabel('time [sec]')
  ylabel('amplitude')
  title(['time domain ',name,'  fs=',int2str(fs)],'interpreter','none')
end
%% PSD
if 0
  figure(2),clf(2)
  f = fs/N*[-N/2:-1,0:N/2-1]';
  F = fft(sig);
  plot(f, 20*log10(abs(fftshift(F))))
  xlabel('frequency [Hz]')
  ylabel('amplitude [dB]')
  title(['frequency domain ',name],'interpreter','none')
  xlim([14990,15010])
  ylim([0,100])
end
%% spectrogram
if 1
  dt = 0.01; %seconds between time steps to plot (arbitrary)
  dtw = 2*dt; % seconds to window
  tstep = ceil(dt*fs);  wind = ceil(dtw*fs);

  figure(3),clf(3)
  specgram(sig, 2^nextpow2(wind),fs,wind,wind-tstep);

  colorbar
  %ylim([14990,15010])
end

end
