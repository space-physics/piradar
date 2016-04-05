=========
 piradar
=========

Using the Raspberry Pi as a radar transmitter and RTL-SDR as receiver.
Raspberry Pi 2 or 3 strongly suggested as CPU needs are substantial.

Current work by others on ``rpitx`` is to import it as a python module instead of the Popen shell call. We should do that instead of Popen.

Install
=======
On your Raspberry Pi::

    sudo ./setup.sh
    

Example
=======
Synthesize a narrowband BPSK waveform and transmit at 100.1MHz center frequency::
    
    ./create_waveform.py 


TODO
====

* Incorporate RTL-SDR on the Raspberry Pi.
