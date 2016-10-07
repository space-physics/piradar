=========
 piradar
=========

`Project Wiki <https://github.com/scienceopen/piradar/wiki>`_

`Executive summary <https://www.scivision.co/pi-radar/>`_

Using the Raspberry Pi as a radar transmitter and RTL-SDR as receiver.
Raspberry Pi 3 strongly suggested as CPU needs are substantial.


.. contents::

Install
=======
On your Raspberry Pi (it will ask for sudo password)::

    ./setup_raspberrypi.sh
    
    ./setup.py develop
    
Or on your PC::

    ./setup.py develop
    

Examples
========
Transmitting on air requires a Raspberry Pi. 
You can just generate the waveforms in memory or to disk on your PC.

Transmit BPSK @ 100.1MHz center frequency
-----------------------------------------
::
    
    ./create_waveform.py -f 100.1
    
Generate BPSK waveform in RAM and plot spectrum
-----------------------------------------------
::

    ./create_waveform.py
    
Progress
========

* Raspberry Pi module has been added to https://github.com/jvierine/digital_rf
* can use https://github.com/jvierine/gr-drf


TODO
====

* Incorporate RTL-SDR on the Raspberry Pi.

* Current work by others on ``rpitx`` is to import it as a python module instead of the Popen shell call--should do that instead of Popen.

Instantaneous Bandwidth
=======================

Raspberry Pi 1b: 1MHz bandwidth too much, 100kHz bandwidth seemed OK.
