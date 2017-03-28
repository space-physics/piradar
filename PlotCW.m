% used with GNU Radio  .bin recordings of CW data from 28 March 2017 experiments
% Michael Hirsch
function PlotCW()
fs = 100000; % Hz, a priori

fnbg = 'data/cw_RX_nothing_new.bin';
fn = 'data/cw_RX_air_2wire.bin';

[~,name,ext] = fileparts(fn);

%% load data
fid = fopen(fnbg,'r');
bg = fread(fid,'float32=>float32');
fclose(fid);

fid = fopen(fn,'r');
dat = fread(fid,'float32=>float32');
fclose(fid);
%% process

doplot(dat,[name,ext],fs)

end 

function doplot(dat,name,fs)

N = length(dat);
F = fft(dat);
f = fs/N*[-N/2:-1,0:N/2-1]';
%% plot
t = 0:1/fs:N/fs;

figure
%plot(t(i),dat(i))
%ylim([-0.0025,0.0025])
xlabel('time [sec]')
ylabel('amplitude [normalized]')
title(['time domain ',name],'interpreter','none')

figure
plot(f, 20*log10(abs(fftshift(F))))
xlabel('frequency [Hz]')
ylabel('amplitude [dB]')
title(['frequency domain ',name],'interpreter','none')
xlim([14990,15010])
ylim([0,100])

end