#!/bin/bash

pip install -r ./requirements.text || { echo "Cannot install required python packages" && exit -1; }
sudo apt-get install python-pyaudio sox flac libportaudio-dev || { echo "Cannot install required debian packages" && exit -1; }
echo "IMPORTANT! run raspi-config to enable serial interface and reboot (only the serial interface, without bash login)"