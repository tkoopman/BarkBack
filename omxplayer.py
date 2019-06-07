############################################################
#         Bark Back: Monitor & Interact with Pets!         #
############################################################
# Code rewritten by Tim Koopman
# Original code written by jenfoxbot <jenfoxbot@gmail.com>
# Code is open-source, coffee/beer-ware license.
# Please keep header + if you like the content,
# buy me a coffee and/or beer if you run into me!
############################################################

import os
from pathlib import Path
import random
import subprocess
from threading import Thread

# Plays random audio files from a folder
class OMXPlayer:
    # Play the selected song and wait for it to finish
    def _call_omxplayer(self, song, vol):
        pid = subprocess.Popen(['omxplayer', '--adev', self.adev, '--vol', str(vol),
                                song], stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        pid.wait()
        self.is_playing = False
    
    # All songs available in the folder
    def songs(self):
        return [self.path + '/' + x for x in os.listdir(self.path) if (x.endswith(self.extensions))]
    
    # Pick a random song from all songs available
    def song(self):
        return random.choice(self.songs())
    
    # Picks a random song and plays it.
    # Returns the selected song's file name or
    # None if a song is already playing.
    # Value is returned immediately and doesn't 
    # wait for the song to complete
    # vol
    #    Override default vol with this vol.
    def play(self, vol=None):
        if not self.is_playing:
            self.is_playing = True
            song = self.song()
            if vol is None:
                vol = self.vol
            self.song_thread = Thread(target=self._call_omxplayer, args=(song,vol,))
            self.song_thread.start()
            return song
    
    # Join the thread playing the current song
    # and wait for it to complete.
    def join(self):
        if self.is_playing:
            self.song_thread.join()
    
    # path
    #    The folder where all the song files are located.
    # extensions
    #    A tuple of valid audio file extensions. Only files 
    #    with these extensions will be used.
    #    Default: .aac, .flac, .mp3, .m4a, .wav
    # adev
    #    The audio device used by OMXPlayer to play the songs
    #    Default: local (3.5mm audio jack)
    # vol
    #    Default volume value passed to OMXPlayer. Read OMXPlayer help for details.
    #    Default: 0
    def __init__(self, path, extensions=(".aac", ".flac", ".mp3", ".m4a", ".wav"), adev="local", vol=0):
        self.adev = adev
        self.extensions = extensions
        self.path = os.path.abspath(path)
        self.vol = vol
        self.is_playing = False
        
        if (not os.path.isdir(path)):
            raise Exception('Path "{}" does not exist or is not a directory'.format(path))
        
        if (len(self.songs()) == 0):
            raise Exception('Path "{}" does not contain any audio files'.format(path))
        
# Test class by playing a random song from current directory
def main():
    player = OMXPlayer(".")
    song = player.play()
    print("Playing: " + song)
    song = player.play()
    if song is not None:
       print("This should not happen")
    
    player.join()
  
if __name__== "__main__":
    main()
