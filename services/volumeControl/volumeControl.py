import alsaaudio

class VolumeControl:
    def __init__(self,intentMessage):
        self.language = intentMessage["language"]

        #for some this can be Master instead of PCM if you get errors try Master
        try:
            self.alsaaudioMixer = alsaaudio.Mixer('PCM')
        except Exception as ex:
            self.alsaaudioMixer = alsaaudio.Mixer('Master')
        self.beforeMuting = self.alsaaudioMixer.getvolume()[0]
        self.volume = self.alsaaudioMixer.getvolume()[0]


    def muteVolume(self):
        print('mute', self.beforeMuting)
        self.beforeMuting = self.alsaaudioMixer.getvolume()[0]
        self.volume = 0
        self.alsaaudioMixer.setvolume(0)

    def unMuteVolume(self):
        print('un mute', self.beforeMuting)
        self.volume = self.beforeMuting
        self.alsaaudioMixer.setvolume(self.beforeMuting)

    def setVolume(self, volume):
        if volume > 0:
            volume = int(volume / 10) * 10
        self.volume = volume
        self.beforeMuting = self.getRealVolume(volume)
        self.alsaaudioMixer.setvolume(self.getRealVolume(volume))
        return self.language["setVolume"].format(volume)

    def getVolume(self):
        return self.alsaaudioMixer.getvolume()[0]

    def increaseVolume(self):
        return self.setvolume(min(100,self.getVolume + 10))

    def decreaseVolume(self):
        return self.setvolume(min(100, self.getVolume - 10))

    # it seems one needs to map the PCM to get the real %  see:
    # https://forum-raspberrypi.de/forum/thread/42097-lautstaerke-per-befehl-aendern/#
    def getRealVolume(self, volume):
        switcher = {
            0: 0,
            2: 0,
            10: 43,
            20: 60,
            30: 70,
            40: 77,
            50: 83,
            60: 87,
            70: 91,
            80: 94,
            90: 97,
            100: 100
        }
        return switcher.get(volume)

