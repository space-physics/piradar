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
    
    python setup.py develop
    
Or on your PC::

    python setup.py develop
    

Examples
========
Transmitting on air requires a Raspberry Pi. 
You can just generate the waveforms in memory or to disk on your PC.

Transmit phase modulation @ 100.1MHz center frequency
-----------------------------------------
::
    
    ./create_waveform.py -f 100.1
    
Generate phase modulation in RAM and plot spectrum
-----------------------------------------------
::

    ./create_waveform.py
    

GNU Radio
=========
The ``.grc`` are for GNU Radio Companion, the graphical IDE.


Simulate BPSK transceiver
-------------------------
Note, this is not the CDMA waveform, just for testing/understanding how to send/receive phase modulated signals.::

    gnuradio-companion PSK_sim.grc

* "signal source" is simulating a DDS
* "multiply" is simulating DUC.
* "rational resampler" controls how fast the bits are played back and hence the instantaneous bandwidth of the signal.
* "multiply const" controls the transmitter power. It would need to be like 0.01 or less to avoid overloading the Red Pitaya input if connecting output to input.

Actual BPSK transceiver with `Red Pitaya <https://www.scivision.co/red-pitaya-gnuradio-setup/>`_
---------------------------------------
::

    gruradio-companion PSK_red-pitaya.grc



Reference
=========

* Raspberry Pi module has been added to https://github.com/jvierine/digital_rf
* can use https://github.com/jvierine/gr-drf


