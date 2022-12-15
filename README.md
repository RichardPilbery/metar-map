# metar-map
Python-based metar map software

# Installation

sudo raspi-config. - set wifi
sudo apt update && sudo apt upgrade
sudo apt install git
sudo apt install python3-pip
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo pip3 install pandas
sudo apt install libatlas-base-dev

# Set up crontab

*/5 7-21 * * *  sudo kill `pgrep python`; sudo python /home/pi/metar.py




# RaspiWiFi

Use Buster Lite build - means you have to use python3

git clone github.com/RichardPilbery/RaspiWiFi.git  (I've forked a copy)

Errors about cryptography, but otherwise it works!

# Couldn't get it to work. Abandoned and will try to roll my own.


# OLED display

https://www.youtube.com/watch?v=lRTQ0NsXMuw&ab_channel=MichaelKlements
https://www.the-diy-life.com/add-an-oled-stats-display-to-raspberry-pi-os-bullseye/

NOTE: May need to install i2c tools too: sudo apt install i2c-tools





