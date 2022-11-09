#!/bin/sh
sudo apt update -y
sudo apt upgrade -y
wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python3 /tmp/get-pip.py
python3 -m pip install --user --upgrade pip wheel setuptools
python3 -m pip install --user -r "dependencies.txt"
