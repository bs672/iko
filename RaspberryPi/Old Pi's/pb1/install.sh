#!/bin/bash
# type in ./install.sh
set -e

# sudo mv /boot/iko7* /home/pi/iko7

# Add network settings
sudo bash -c 'cat default_networks.txt >> /etc/wpa_supplicant/wpa_supplicant.conf'

cd /home/pi

# Update apt
sudo apt-get update
sudo apt-get -y upgrade

# Install dependencies
sudo apt-get install -y python-pip
sudo pip install paho-mqtt
sudo pip install pytz
sudo apt install python3-gpiozero python3-pigpio
sudo apt install python-gpiozero python-pigpio
sudo apt install pigpio
sudo systemctl enable pigpiod
sudo apt-get install -y git
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install
cd ..
git clone https://github.com/aws/aws-iot-device-sdk-python.git
cd aws-iot-device-sdk-python
sudo python setup.py install
cd /home/pi
# sudo apt-get install -y subversion
# svn checkout https://github.com/bs672/petal-code/raspberrypi/trunk/iko$1
# git clone https://github.com/bs672/petal-code/raspberrypi/iko$1.git

# Set program to launch on startup
sed 's/exit 0/cd /home/pi/iko\npython /home/pi/iko/automatino_oo.py 1 0 &\nexit 0' /etc/rc.local

sudo reboot