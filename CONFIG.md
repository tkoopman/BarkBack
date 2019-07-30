# bark_back.cfg
Config is stored in an INI file format. If you currently do not have a config file
you can run bark_back.py and it will generate a default config file.

## [OMXPlayer]
### path = .
This is the path to your songs folder.

### vols = 0,1000,2000,3000
This is a comma seperate list of OMXPlayer volumes to use in order from quitest to loudest.
Volume will increase as the number of barks detected over a period of time increases, until max volume.

Please refer to OMXPlayer manual for details on vol values.

### vol_period = 300
Number of seconds over which is more barks are detected the volume will increase.

### adev = local
The audio device OMXPlayer will use.

Please refer to OMXPlayer manual for details on adev values.

### extensions = .aac,.flac,.mp3,.m4a,.wav
A comma seperated list of file extensions that can be used to play songs in OMXPlayer.
Only files with these entensions in the songs folder will be used.

## [Monitor]
### adc_channel = 0
This is the channel on the MCP3002 chip to read the mic values from. 

### spi_channel = 0
SPI Channel on Raspberry Pi to used
* 0 = (CE0 / GPIO08 Pin)
* 1 = (CE1 / GPIO07 Pin)

### high_volume = 50
This is used to calculated the number of barks detected over a period of time. 
Valid values are 0 - 100.

### high_volume_period=5
Number of seconds that high volume is tracked over

### high_volume_max=4
Max times high volume can be detected during the high_volume_period seconds before triggering song.

### sample_time=0.05
Time in seconds that the mic is polled for to calculate the current amplitude (volume)

### hz=10
Times per second to poll the mic's amplitude

## [Logging]
### level=INFO
stdout logging level.
* ERROR = Only errors
* INFO = Songs played & service starting
* DEBUG = Volume levels every 1 second

## [CloudMQTT]
### enabled=no
Enable CloudMQTT integration. If enabled you must fill in the instance details below.

### tls=yes
Use TLS encryption

### host=postman.cloudmqtt.com
CloudMQTT instance host/server name.

### port
CloudMQTT instance port number

### user
CloudMQTT instance user name

### password
CloudMQTT instance password

### topic_volume=Volume
Topic to use to publish volume levels every 1 second. Leave blank to not send volume data.

### topic_playing=Playing
Topic to publish when a song is being played. Leave blank to not send song details.

### topic_play=Play
Topic to subscribe to so you can trigger manually to play a random song. 
Payload can include an interger value which will be used for the OMXPlayer volume.

## [syslog]
### enabled=no
Enable sending data to remote syslog server. If enabled you must configure syslog server details below.

### level=DEBUG
Syslog logging level.
* ERROR = Only errors
* INFO = Songs played & service starting
* DEBUG = Volume levels every 1 second

### host
Syslog server

### port
Syslog UDP port number
