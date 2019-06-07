# Installation
This has been tested with fresh install of raspbian stretch lite.
If you don't want it installed to /home/pi/BarkBack/ you may need
to change some commands or files below.

## After first boot
Change default password using `pwd`

Update OS and install packages
```
sudo apt-get update
sudo apt-get upgrade -y
sudo reboot
sudo apt-get install -y git omxplayer
```

Enable SPI by running `sudo raspi-config` and under Interface Options select the SPI option to enable.

## Python2 Modules
If you want to use Python2 install the following.
```
sudo apt-get install -y python-pip
pip install configparser spidev statistics pathlib paho-mqtt

```

## Python3 Modules
If you want to use Python3 install the following.
```
sudo apt-get install -y python3-pip
pip3 install spidev paho-mqtt
```

## Download Bark Back
```
cd /home/pi
git clone https://github.com/tkoopman/BarkBack.git
cd BarkBack
python3 bark_back.py
```
This should start and create the [default configuration](CONFIG.md) and exit due to no music files found.

Now all you have to do is edit bark_back.cfg and add music files to ~/BarkBack/ 
folder (or the folder you specify in the config file)

## Start on boot
Run the following to start the program on boot
```
sudo cp /home/pi/BarkBack/bark_back.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/bark_back.service
sudo systemctl daemon-reload
sudo systemctl enable bark_back
sudo systemctl start bark_back
sudo systemctl status bark_back
```
