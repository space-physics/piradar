from io import BytesIO
import subprocess
"""
for transmitting from Raspi GPIO, not used anymore.
"""
def transmit_raspi(tx,fs,freqmhz):
    print('Attempting transmission on {} MHz'.format(freqmhz))
    # on raspberry pi, sudo does not require reentering password via default /etc/sudoers configuration
    P = BytesIO()
    P.write(tx) #have to do as two lines of code

    cmd = ['sudo', 'rpitx','-mIQ','-s{}'.format(fs),'-i-','-f',str(freqmhz*1e3)]
    print(' '.join(cmd))

    p = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    p.communicate(input=P.getvalue())