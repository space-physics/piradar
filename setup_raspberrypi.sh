#!/bin/bash

# Michael Hirsch
# setups the environment for Raspberry Pi Radar

# 0) be sure it's not running on your laptop
if ! uname -m | grep -q arm; then 
    echo "this script is meant to be run on your Raspberry Pi"
    exit 1
fi

# 1) prereqs
sudo apt install git gcc make

# 2) copy and install the GPIO code to transmit
git clone https://github.com/F5OEO/rpitx
cd rpitx
sudo ./install.sh


