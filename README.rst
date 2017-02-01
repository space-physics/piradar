=========
 piradar
=========

`Project Wiki <https://github.com/scienceopen/piradar/wiki>`_

`Executive summary <https://www.scivision.co/pi-radar/>`_

Radar using Red Pitaya for RF and Raspberry Pi 3 for quad-core signal processing. 
Initially used for ionospheric imaging at HF but via frequency translation could be used at microwave and other frequencies.

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

    git clone https://github.com/pavel-demin/red-pitaya-notes

    cd red-pitaya-notes/projects/sdr_transceiver/gnuradio

Each time you start the program (or put into a Bash script)::

    export GRC_BLOCKS_PATH=.
    gnuradio-companion

   

Examples
========
You can just generate the waveforms in memory or to disk on your PC.
    
Generate phase modulation in RAM and plot spectrum
--------------------------------------------------
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
------------------------------------------------------------------------------------------------
::

    gruradio-companion PSK_red-pitaya.grc



Reference
=========

* Raspberry Pi module has been added to https://github.com/jvierine/digital_rf
* can use https://github.com/jvierine/gr-drf

Obsolete: Raspberry Pi Transmit code Install
--------------------------------------------
We use the Red Pitaya to transmit instead.
The program below uses Rpi GPIO to transmit waveforms, but we found the jitter way too high to use for radar.

On your Raspberry Pi (it will ask for sudo password)::

    ./setup_raspberrypi.sh
    
    python setup.py develop
    
Or on your PC::

    python setup.py develop

Obsolete: Raspi transmit PM centered @ 100.1MHz 
-----------------------------------------------
::
    
    ./create_waveform.py -f 100.1


