% used with GNU Radio  .bin recordings of CW data from 28 March 2017 experiments
% of course, these recordings are after DDC.
% Issue with CW Nulling appears to include that recordings weren't coherent, frequency drifted, etc. from BG recording to target recording.
% Michael Hirsch, Ph.D.
function PlotCW()
 try % for GNU Octave
  pkg load signal
 end
%% user parameters

%Anull = 1.6;
%phi = 0.275; % [radians] the amount of phase shift for manual CW nulling
%Anull=1;
%phi=-0.37;

fs = 100000; % Hz, a priori
%i = 1:500000;
i = 500000:1100000; % beginning of signal times
%i = 500000:500100; % manual nulling view

%fnbg = 'data/cw_RX_nothing_new.bin';
fn = 'data/cw_RX_air_2wire.bin';

[~,name,ext] = fileparts(fn);
t = i(1)/fs:1/fs:i(end)/fs;
%% load data
%fid = fopen(fnbg,'r');
%bg = fread(fid,'float32=>float32');
%fclose(fid);

fid = fopen(fn,'r');
sig = fread(fid,'float32=>float32');
fclose(fid);
%% process
% extract wanted time segment of signal (so don't always have to work with entire file)
%bg = bg(i); 
%ibg=10000;
%bg = sig(ibg:length(t)+ibg-1);
sig = sig(i);

% attempt manual CW nulling -- not working, need true coherent simultaneous sample which we don't have.
%zbg = fft(bg);
%N = length(zbg);
%for k = 1:N
%  w = 2*pi/N*(k-1);
%  sbg(k) = zbg(k)*exp(-1j*w*phi);  
%end
%bg = real(ifft(sbg))';
%sigsub = sig - Anull*bg;

%sigsub = sig - bg;

radarplot(sig,t,[name,ext],fs)

end 

function radarplot(sig,t,name,fs)

N = length(sig);

%% plot
if 1
  figure(1),clf(1),hold('on')
  %plot(t,bg,'r','displayname','background')
  plot(t,sig,'b','displayname','raw signal')
 % plot(t,sigsub,'k','displayname','BG subtracted signal','linewidth',2)
  %ylim([-0.0025,0.0025])
  xlabel('time [sec]')
  ylabel('amplitude [normalized]')
  title(['time domain ',name],'interpreter','none')
  legend('show')
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
  specgram(sig, 2^nextpow2(wind),fs,wind,wind-tstep);
  
  colorbar
  ylim([14990,15010])
end

end