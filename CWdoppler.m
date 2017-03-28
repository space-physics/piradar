% Simulate Doppler spectrum

fc = 15e3; %[Hz]
Ac = 0.5;

fb = fc + 3; %[Hz]
Ab = 0.5;

fs = 100e3; %[Hz]
t = 0:1/fs:1-1/fs;

xc = Ac*sin(2*pi*fc*t);
yc = Ab*sin(2*pi*fb*t);


dat = xc+yc;
%% Time
figure(1); clf(1)
plot(t,dat)
xlabel('time [sec]')
ylabel('amplitude')

%% spectrogram
figure(2);clf(2)
try % for GNU Octave
pkg load signal
end

dt = 0.35; %seconds between time steps to plot (arbitrary)
dtw = 2*dt; % seconds to window
tstep = ceil(dt*fs);
wind = ceil(dtw*fs);
Nfft = 2^nextpow2(wind);

figure(2);clf(2)
specgram(dat,Nfft,fs,wind,wind-tstep);

colorbar
ylim([14990,15010])
%% periodogram
figure(3); clf(3)
pwelch(dat,wind,0.5,Nfft,fs)
xlim([14990,15010])