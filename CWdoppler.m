function CWdoppler()
% Simulate Doppler spectrum
try % for GNU Octave
  pkg load signal
end

% recall DFT is samples of continuous DTFT
zeropadfactor = 1; %arbitrary, expensive way to increase DFT resolution. 
% eventually you'll run out of RAM if you want arbitrarily high precision

fb0 = 3; % Hz  arbitrary "true" Doppler frequency saught.
t1 = 1; % final time, t0=0 seconds
An = 0.1; % standard deviation of AWGN

ft = 15e3; %[Hz]
At = 0.5;

fb = ft + fb0; %[Hz]
Ab = 0.1;

fs = 100e3; %[Hz]
t = 0:1/fs:t1-1/fs;

xt = At*sin(2*pi*ft*t);
xbg = xt + An*randn(size(xt)); % we receive the transmitter with noise
% compute beat frequency 
xb = Ab*sin(2*pi*fb*t);
% compute noisy, jammed observatoin
y = xb + xbg + An*randn(size(xbg)); % each time you receive, we assume i.i.d. AWGN
%% Time
figure(1); clf(1)
plot(t,y)
xlabel('time [sec]')
ylabel('amplitude')

%% background subtract
ysub = y-xbg;

%% spectrogram
dt = 0.45; %seconds between time steps to plot (arbitrary)
dtw = 2*dt; % seconds to window
tstep = ceil(dt*fs);
wind = ceil(dtw*fs);
Nfft = 2^nextpow2(zeropadfactor*wind); 

if 0
figure(2);clf(2)
specgram(ysub,Nfft,fs,wind,wind-tstep);
colorbar
ylim([14990,15010])
end
%% periodogram
figure(3), clf(3), hold('on')

[Sraw,f] = pwelch(y,wind,0.5,Nfft,fs);
plot(f,Sraw,'r')

[Ssub,f] = pwelch(ysub,wind,0.5,Nfft,fs);
plot(f,Ssub)

xlim([14990,15010])
xlabel('frequency [Hz]')
ylabel('amplitude')
legend('raw','bg subtract')

%set(axsub,'ylim',get(axraw,'ylim'))
%% find target beat frequency
[pks,loc] = findpeaks(Ssub,...
            'minpeakdistance',5,... % minpeak distance speeds up computation
            'minpeakheight',0.01*max(Ssub)); 
plot(f(loc),pks,'k*','markersize',12)

title(['Periodogram: Nfft=',int2str(Nfft),'.  f_b = ',num2str(f(loc(1))-ft,'%.3f'),' Hz.'])

end