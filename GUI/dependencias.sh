#!/bin/bash

# Instala python
sudo apt update
sudo apt install python3 -y

# Instala Tkinter 
sudo apt install python3-tk -y
# Instala ImageTk 
sudo apt-get install python3-pil.imagetk
sudo apt-get -y install socat
sudo apt install pip
python3 -m pip install psutil
#GDB
sudo apt-get install gdb-multiarch

echo "Installation complete."
