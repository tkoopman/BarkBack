############################################################
#         Bark Back: Monitor & Interact with Pets!         #
############################################################
# Code rewritten by Tim Koopman
# Original code written by jenfoxbot <jenfoxbot@gmail.com>
# Code is open-source, coffee/beer-ware license.
# Please keep header + if you like the content,
# buy me a coffee and/or beer if you run into me!
############################################################

from collections import deque
import spidev
import statistics
import threading
import time

def _bitstring(n):
    s = bin(n)[2:]
    return '0'*(8-len(s)) + s

# Function to map peak-to-peak amp to a volume unit between 0 and 100
def _volume_unit(data, fromLow=0, fromHigh=1023, toLow=0, toHigh=100):
    return (data - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow

# monitor class used to continuously poll the MIC
#
# Main Properties
#   monitor.volume
#     The volume (0 - 100) of the last reading.
#   monitor.volume_mean
#     The average volume over the last {stats_over_time} seconds of readings.
#   monitor.volume_high_count
#     The number of times in the last {stats_over_time} seconds the volume
#     was over {volume_high_over} value.
class monitor:
    # Reads current value from the MIC
    def __read(self):
        reply_bytes = self.__spi.xfer2([self.__adc_channel_cmd, 0])
        reply_bitstring = ''.join(_bitstring(n) for n in reply_bytes)
        reply = reply_bitstring[5:15]
        return int(reply, 2)
    
    # Calculates the peak to peak amplitude (volume) over the sample_time period
    def __ptp_amp(self):
        max = 0
        min = 1023
        
        start_time = time.time()
        while(time.time() - start_time < self.sample_time):
            data = self.__read()
            if(data < 1023): #Prevent erroneous readings
                if(data > max):
                    max = data
                elif(data < min):
                    min = data
        
        return max - min

    # Main thread the polls the MIC and calculates the volume
    def __run(self):
        while self.__thread_state == 0:
            self.volume = _volume_unit(self.__ptp_amp())
            self._highqueue.append(self.volume)
            
            self.high_volume_count = sum(1 for vol in self._highqueue if vol >= self.high_volume)
            if self.high_volume_count >= self.high_volume_max:
                self._highqueue.clear()
                if self.on_high_volume is not None:
                    thread = threading.Thread(target=self.on_high_volume, args=())
                    thread.daemon = True
                    thread.start()
            time.sleep(self.sleep_time)
        
        self.__thread_state = 2

    # adc_channel
    #    Channel on the MCP3002 chip to read mic values from.
    #    Default: 0 (CH0 Pin)
    # spi_channel
    #    SPI Channel on Raspberry Pi to used
    #    Default: 0 (CE0 / GPIO08 Pin)
    # high_volume
    #    Any volume level over this is classed as high when calculating
    #    the monitor.volume_high_count property
    #    Default: 50
    # high_volume_period
    #    Time in seconds to collate polled mic data and calculate the monitor.volume_high_count over.
    #    Default: 5
    # high_volume_max
    #    When this number of high volumes happen over the high_volume_period, the on_high_volume event will be triggered.
    #    Default: 4
    # on_high_volume
    #    Function to trigger when high_volume_max it hit
    # sample_time
    #    Time in seconds that the mic is polled to find the current amplitude
    #    Default: 0.05
    # sleep_time
    #    Time in seconds to sleep between polling the mic's amplitude
    #    Default: 0.1
    def __init__(self, adc_channel=0, spi_channel=0, high_volume=50, high_volume_period=5, high_volume_max=4, on_high_volume=None, sample_time=0.05, sleep_time=0.1):
        self.__adc_channel_cmd = 128
        if adc_channel:
            self.__adc_channel_cmd += 32
        self.sample_time = sample_time
        self.sleep_time = sleep_time
        self.high_volume = high_volume
        self.high_volume_max = high_volume_max
        self.__spi = spidev.SpiDev(0, spi_channel)
        self.__spi.max_speed_hz = 1200000 # 1.2 MHz

        self._highqueue = deque([], round(high_volume_period / (sample_time + sleep_time)))
        self.volume = 0
        self.high_volume_count = 0
        self.on_high_volume = on_high_volume
        
        self.__thread_state = 0
        self.__thread = threading.Thread(target=self.__run, args=())
        self.__thread.daemon = True
        self.__thread.start()
    
    # Should be called when monitor is no longer required
    # Stops the polling and closes SPI connection
    def close(self):
        self.__thread_state = 1
        self.__thread.join()
        self.__spi.close()

# Test class code.
# Polls mic and outputs data over 10 seconds.
def main():
    def on_high_vol():
        print("High Volume Triggered")

    m = monitor(on_high_volume=on_high_vol)
    print("vol high_count")
    for _ in range(10):
        print("% 3d  % 3d" %(m.volume, m.high_volume_count))
        time.sleep(1)
    
    m.close()
  
if __name__== "__main__":
    main()
