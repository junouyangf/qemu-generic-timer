#!/bin/bash

# Instala python
sudo apt update
sudo apt install python3 -y

# Instala Tkinter 
sudo apt install python3-tk -y

# Instala ImageTk 
sudo apt-get install python3-pil.imagetk
sudo apt-get -y install socat

sudo apt install python3-dev -y
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py
sudo pip3 install pexpect
sudo pip install --upgrade psutil

echo "Installation complete."
