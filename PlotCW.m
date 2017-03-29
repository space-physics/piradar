% used with GNU Radio  .bin recordings of CW data from 28 March 2017 experiments
% of course, these recordings are after DDC.
% Michael Hirsch, Ph.D.
function PlotCW()
 try % for GNU Octave
  pkg load signal
 end
%% user parameters
fs = 100000; % Hz, a priori
%i = 1:500000;
%i = 500000:1100000; % beginning of signal times
i = 500000:500100;

fnbg = 'data/cw_RX_nothing_new.bin';
fn = 'data/cw_RX_air_2wire.bin';

[~,name,ext] = fileparts(fn);

%% load data
fid = fopen(fnbg,'r');
bg = fread(fid,'float32=>float32');
fclose(fid);

fid = fopen(fn,'r');
sig = fread(fid,'float32=>float32');
fclose(fid);
%% process
t = i(1)/fs:1/fs:i(end)/fs;
radarproc(bg(i),sig(i),t,[name,ext],fs)

end 

function radarproc(bg,sig,t,name,fs)

N = length(sig);
%% background subtraction
sigsub = sig-bg;
%% plot

if 1
  figure(1),clf(1),hold('on')
  plot(t,bg,'r')
  plot(t,sig,'b')
  %ylim([-0.0025,0.0025])
  xlabel('time [sec]')
  ylabel('amplitude [normalized]')
  title(['time domain ',name],'interpreter','none')
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
if 0
  dt = 0.1; %seconds between time steps to plot (arbitrary)
  dtw = 2*dt; % seconds to window
  tstep = ceil(dt*fs);  wind = ceil(dtw*fs);
  
  figure(3),clf(3)
  specgram(sigsub, 2^nextpow2(wind),fs,wind,wind-tstep);
  
  colorbar
  ylim([14990,15010])
end

end