############################################################
#         Bark Back: Monitor & Interact with Pets!         #
############################################################
# Code rewritten by Tim Koopman
# Original code written by jenfoxbot <jenfoxbot@gmail.com>
# Code is open-source, coffee/beer-ware license.
# Please keep header + if you like the content,
# buy me a coffee and/or beer if you run into me!
############################################################

# Many thanks to the folks who create & document the libraries
# and functions used in this project.

from collections import deque
from collections import OrderedDict
import configparser
import logging
from logging.handlers import SysLogHandler
from syslog_rfc5424_formatter import RFC5424Formatter
from monitor_mic import monitor
from omxplayer import OMXPlayer
import os.path
import paho.mqtt.client as paho
import socket
import ssl
import sys
import time

def main():
    global logger
    logger = logging.getLogger("BarkBack")
    logger.setLevel('DEBUG')
    stdout = logging.StreamHandler(stream=sys.stdout)
    stdout.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %I:%M:%S %p'))
    logger.addHandler(stdout)
    
    ReadConfig()
    InitLogger()
    InitMQTTC()

    global player_volumes
    player_volumes = tuple(int(x) for x in config['OMXPlayer']['vols'].split(','))

    global player
    player = OMXPlayer(path       = config['OMXPlayer']['path'],
                       extensions = tuple(config['OMXPlayer']['extensions'].split(',')),
                       adev       = config['OMXPlayer']['adev'],
                       vol        = player_volumes[0])

    mic = monitor(adc_channel        = config['Monitor'].getint('adc_channel'),
                  spi_channel        = config['Monitor'].getint('spi_channel'),
                  high_volume        = config['Monitor'].getint('high_volume'),
                  high_volume_period = config['Monitor'].getint('high_volume_period'),
                  high_volume_max    = config['Monitor'].getint('high_volume_max'),
                  on_high_volume     = on_high_volume,
                  sample_time        = config['Monitor'].getfloat('sample_time'),
                  Hz                 = config['Monitor'].getint('hz'))

    global last_events
    last_events = deque([], len(player_volumes)-1)

    # This loop main purpose is:
    #    Keep program running
    #    Output DEBUG volume data
    #    Poll MQTTC for subscribed topics
    while True:
        time.sleep(1)
        logger.debug("volume_avg=%1.3f volume_max=%d high_count=%d" %(mic.volume_avg, mic.volume_max, mic.high_volume_count), {'msgid': 'volume'})
        mqttc_publish(config['CloudMQTT']['topic_volume'], '{"Average":%1.3f,"Max":%d,"High_Count":%d}' %(mic.volume_avg, mic.volume_max, mic.high_volume_count))
        mqttc_loop()

# This is triggered when barking is detected by mic monitor thread
def on_high_volume():
    vol = player_volumes[(sum(1 for e in last_events if time.time() - e <= config['OMXPlayer'].getint('vol_period')))]
    last_events.append(time.time())
    play_song(vol)

def play_song(vol):
    if (vol > player_volumes[-1]):
        vol = player_volumes[-1]

    song = player.play(vol=vol)
    if song is not None:
        logger.info("playing=%s volume=%s" %(song, vol), {'msgid': 'play'})
        mqttc_publish(config['CloudMQTT']['topic_playing'], '{"Song":"%s","Vol":%s}' %(song, vol))
        player.join()
        mqttc_publish(config['CloudMQTT']['topic_playing'], "")

def InitLogger():
    # Set console (stdout) logging level
    logger.handlers[0].setLevel(config['Logging']['level'])

    if config['syslog'].getboolean('enabled'):
        syslog = SysLogHandler(address=(config['syslog']['host'], config['syslog'].getint('port')), facility=SysLogHandler.LOG_USER, socktype=socket.SOCK_DGRAM)
        syslog.setFormatter(RFC5424Formatter())
        syslog.setLevel(config['syslog']['level'])
        logger.addHandler(syslog)

    logger.info("starting", {'msgid': 'info'})

def InitMQTTC():
    global mqttc
    if config['CloudMQTT'].getboolean('enabled'):
        mqttc = paho.Client()
        if config['CloudMQTT'].getboolean('tls'):
            mqttc.tls_set_context(ssl.create_default_context())
        mqttc.on_message = on_message
        mqttc.username_pw_set(config['CloudMQTT']['user'], config['CloudMQTT']['password'])
        mqttc.connect(config['CloudMQTT']['host'], config['CloudMQTT'].getint('port'))
        if config['CloudMQTT']['topic_play'] not in (None, ''):
            mqttc.subscribe(config['CloudMQTT']['topic_play'], 0)
    else:
        mqttc = None

def mqttc_publish(topic, data):
    if mqttc is not None:
        if topic not in (None, ''):
            mqttc.publish(topic, data)
            mqttc.loop_write()

# MQTTC message received on subscribed topic
def on_message(mosq, obj, msg):
    logger.debug("mqttc: topic=%s payload=%s" %(msg.topic, msg.payload))
    if (msg.topic == config['CloudMQTT']['topic_play']):
        try:
           vol = int(msg.payload)
        except ValueError:
           vol = player_volumes[0]

        play_song(vol)

# Checks for new data to send/receive
def mqttc_loop():
    if mqttc is not None:
        while mqttc.loop():
            time.sleep(0.05)

def ReadConfig():
    config_file='./bark_back.cfg'
    global config
    config = configparser.ConfigParser(dict_type=OrderedDict)
    # Default configuration
    defaultConfig=u"""
    [OMXPlayer]
    path=.
    vols=0,1000,2000,3000
    vol_period=300
    adev=local
    extensions=.aac,.flac,.mp3,.m4a,.wav

    [Monitor]
    adc_channel=0
    spi_channel=0
    high_volume=50
    high_volume_period=5
    high_volume_max=4
    sample_time=0.05
    hz=10

    [Logging]
    level=INFO

    [CloudMQTT]
    enabled=no
    tls=yes
    host=postman.cloudmqtt.com
    port=
    user=
    password=
    topic_volume=Volume
    topic_playing=Playing
    topic_play=Play

    [syslog]
    enabled=no
    level=DEBUG
    host=
    port=
    """
    config.read_string(defaultConfig)
    if os.path.isfile(config_file):
        config.read(config_file)
    else:
        logger.error("Missing configuration file. Using defaults.")
        logger.error("Creating default {}".format(config_file))
        with open(config_file, 'w') as configFile:
            config.write(configFile)

if __name__== "__main__":
    main()
