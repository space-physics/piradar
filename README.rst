=========
 piradar
=========

`Project Wiki <https://github.com/scienceopen/piradar/wiki>`_

`Executive summary <https://www.scivision.co/pi-radar/>`_

Radar using Red Pitaya for RF and Raspberry Pi 3 for quad-core signal processing. 
Initially used for ionospheric imaging at HF but via frequency translation could be used at microwave and other frequencies.

To run the Red Pitaya radar on the bench, you need to

1. generate a binary file containing a psuedorandom phase modulated signal with ``create_waveform``
2. use GNU Radio to read that file and transmit it
3. either on the same or separate Red Pitaya, receive the transmitted waveform and save it to file
4. use a Python (or whatever) script to process the transmit and receive waveforms together e.g. cross-correlation, estimate number of lags to peak.

.. contents::

Setup Red Pitaya Radar software
================================
First you setup an image on the Micro SD card, then you setup GNU Radio on your Linux laptop.

Install Red Pitaya GNU Radio image
----------------------------------
This assumes a brand new Red Pitaya with blank micro SD card.

1. format a micro SD card to FAT32
2. unzip `Pavel Demins SD Card GNU Radio image <https://pavel-demin.github.io/red-pitaya-notes/sdr-transceiver/>`_ (Under "getting started with GNU Radio") to this SD card::

    unzip ecosystem-0.95-1-6deb253-sdr-transceiver.zip -d /media/sd-card

   where ``/media/sd-card`` is the path to the FAT32-formatted SD card on your laptop.
3. boot the Red Pitaya with this micro SD card. login/password ``root``

Install GNU Radio Red Pitaya tools
----------------------------------
On your laptop::

    mkdir ~/code

    cd ~/code

    git clone https://github.com/pavel-demin/red-pitaya-notes

    cd red-pitaya-notes/projects/sdr_transceiver/gnuradio

On your laptop, create a file `~/rpgr` with contents::

    #!/bin/bash
    export GRC_BLOCKS_PATH=$HOME/code/red-pitaya-notes/projects/sdr_transceiver/gnuradio
    gnuradio-companion

Then in the future to startup GNU Radio with the modules for the Red Pitaya, just type on your laptop::

    ~/rpgr

Transmit waveform generation
============================
You can just generate the waveforms in memory or to disk on your PC.
You don't actually need the Red Pitaya to work with these offline, to test your algorithms in the computer alone.

To transmit these waveforms with the Red Pitaya, tell GNU Radio to read the waveform file you generated and transmit it with the appropriate block diagram.
    
Generate phase modulation in RAM and plot spectrum
--------------------------------------------------
plot only, don't save or transmit::

    ./create_waveform.py

-o directory     saves binary psuedorandom phase modulated signal to *directory* for use with GNU Radio
-q               quiet, no plotting
--filter         smoothes transmit waveform, reducing splatter
--fs fsampleHz   sample frequency in Hz of baseband waveform

The following option is for Raspberry Pi only; no longer used

-f frequencyMHz     center frequency in MHz to transmit from Raspberry Pi GPIO


GNU Radio
=========
The ``.grc`` are for GNU Radio Companion, the graphical IDE.


Simulate BPSK transceiver
-------------------------
Note, this is not the CDMA waveform, just for testing/understanding how to send/receive phase modulated signals.::

    ~/rpgr PSK_sim.grc

* "signal source" is simulating a DDS
* "multiply" is simulating DUC.
* "rational resampler" controls how fast the bits are played back and hence the instantaneous bandwidth of the signal.
* "multiply const" controls the transmitter power. It would need to be like 0.01 or less to avoid overloading the Red Pitaya input if connecting output to input.

Actual BPSK transceiver with `Red Pitaya <https://www.scivision.co/red-pitaya-gnuradio-setup/>`_
------------------------------------------------------------------------------------------------
::

    ~/rpgr PSK_red-pitaya.grc



Reference (obsolete)
====================
The material in this section is for using Raspberry Pi as the transmitter, which we no longer use.

* Raspberry Pi module has been added to https://github.com/jvierine/digital_rf
* can use https://github.com/jvierine/gr-drf

Raspberry Pi Transmit Install
-----------------------------
We use the Red Pitaya to transmit instead.
The program below uses Rpi GPIO to transmit waveforms, but we found the jitter way too high to use for radar.

On your Raspberry Pi (it will ask for sudo password)::

    ./setup_raspberrypi.sh
    
    python setup.py develop
    
Or on your PC::

    python setup.py develop

Raspi transmit PM  
-----------------
centered @ 100.1MHz::
    
    ./create_waveform.py -f 100.1


