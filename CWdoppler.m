% Simulate Doppler spectrum

fc = 15e3; %[Hz]
fb = fc + 3; %[Hz]

fs = 100e3; %[Hz]
t = 0:1/fs:1-1/fs;

xc = 0.5*sin(2*pi*fc*t);
yc = 0.1*sin(2*pi*fb*t);


dat = xc+yc;
%% Time
figure(1); clf(1)
plot(t,dat)
xlabel('time [sec]')
ylabel('amplitude')

%% spectrogram
try % for GNU Octave
pkg load signal
end

dt = 0.35; %seconds between time steps to plot (arbitrary)
dtw = 2*dt; % seconds to window
tstep = ceil(dt*fs);
wind = ceil(dtw*fs);

figure
specgram(dat,2^nextpow2(wind),fs,wind,wind-tstep);

colorbar
ylim([14990,15010])
