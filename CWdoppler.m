% Simulate Doppler spectrum

fc = 15e3; %[Hz]
fb = fc + 3; %[Hz]

fs = 100e3; %[Hz]
t = 0:1/fs:1-1/fs;

xc = 0.5*sin(2*pi*fc*t);
yc = 0.1*sin(2*pi*fb*t);

plot(t,xc+yc)