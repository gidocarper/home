#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import fnmatch
from tinytag import TinyTag
import os
import os.path
from os import path
import json
import pygame
import threading, random
NEXT = pygame.USEREVENT + 1
os.environ["SDL_VIDEODRIVER"] = "dummy"

class MuuzikPlayer:
    def __init__(self, intentMessage):
        self.language = intentMessage["language"]
        self.text_to_translate = None
        self.pattern = '*.mp3'
        self.playlist = []
        self.startFirstSongOnce = True
        self.current_track = 0
        self.pathToMusic = '/home/pi/Music'
        self.musicFile = []
        self.backgroundthread = None
        self.running = False
        self.stopTheMusic = False

    def scanMusic(self):
        rootPath = '/home/pi/Music/'
        songlist = []
        numberOfSongsBeforeScan = self.countMySongs()
        artistlist = []
        pattern = '*.mp3'
        for root, dirs, files in os.walk(rootPath):
            for filename in fnmatch.filter(files, pattern):
                if path.exists(os.path.join(root, filename)):
                    try:
                        audiofile = TinyTag.get(os.path.join(root, filename))
                        album = str(audiofile.album)
                        title = str(audiofile.title)
                        genre = str(audiofile.genre)
                        albumArtist = str(audiofile.albumartist)
                        artist = str(audiofile.artist)
                        year = str(audiofile.year)
                        print(audiofile)
                        a = albumArtist
                        if albumArtist == 'None':
                            a = artist

                        if (a) not in artistlist:
                            artistlist.append(a)

                        songlist.append({
                            'song': '{} {} {} {}  {} {}  {} '.format(album, title, genre, albumArtist, artist, year,
                                                                     os.path.join(root, filename)),
                            'path': os.path.join(root, filename)
                        })
                    except:
                        print('error')

        with open('/home/pi/Music/musicFound.json', 'w') as f:
            json.dump(songlist, f, indent=4)
        with open('/home/pi/Music/artistlist.json', 'w') as f:
            json.dump(artistlist, f, indent=4)

        numberOfSongsAfterScan = self.countMySongs()
        if (numberOfSongsAfterScan < numberOfSongsBeforeScan):
            return self.language["removedSongs"].format(numberOfSongsBeforeScan - numberOfSongsAfterScan)
        if (numberOfSongsAfterScan > numberOfSongsBeforeScan):
            return self.language["foundNewSongs"].format(numberOfSongsAfterScan - numberOfSongsBeforeScan)

        #TODO add found artists to slot artists
        #TODO check which songs are new and only add these artists to the artists slot
        #TODO add song titles and albums as slot too

        return self.language["scanningIsDone"]

    def countMySongs(self):
        musicFile = open(self.pathToMusic + '/musicFound.json')
        allSongs= json.load(musicFile)
        musicFile.close()
        return len(allSongs)

    def play(self, intent_message):
        self.playlist = []
        print('play music ' + intent_message)
        if not str(os.path.exists(self.pathToMusic + '/musicFound.json')):
            print('play Musik')
            self.scanMusic()

        if len(self.musicFile) == 0:
            musicFile = open(self.pathToMusic + '/musicFound.json')
            self.musicFile = json.load(musicFile)
            musicFile.close()

        title = ''
        album = ''
        artist = intent_message
        genre = ''

        i = 0
        while i < len(self.musicFile):
            path = self.musicFile[i]['path']
            song = self.musicFile[i]['song']
            i += 1

            if song.find(artist) > 0 \
                    or song.find(album) > 0 \
                    or song.find(title) > 0 \
                    or song.find(genre) > 0:
                self.playlist.append(path)

        self.current_track = 0

        return self.playSong()


    def next(self):
        self.backgroundthread = None
        if self.current_track < len(self.playlist) - 1:
            self.current_track += 1
            self.playSong()
            return self.language['nextSong']
        else:
            self.current_track = 0
            self.stop()
            return self.language['playListEnded']

    def previous(self):
        if self.current_track == 0:
            self.current_track = len(self.playlist) - 1
        else:
            self.current_track -= 1
        self.playSong()
        return self.language['previuosSong']

    #Not implemented yet
    def repeat(self):
        self.playSong()
        return 'okay ich wieder hole'

    def stop(self):
        self.stopTheMusic = True
        pygame.mixer.music.stop()
        pygame.mixer.set_endevent(type)
        pygame.quit()
        self.backgroundthread = None
        return self.language['stoppedTheMusic']


    def playSong(self):
        # I am sure this is not the right way to use a thread but I have no clue how to play the music while
        # continueing the other scripts
        self.backgroundthread = None
        self.backgroundthread = threading.Thread(target=self.playing)
        self.backgroundthread.start()
        return self.language['startedPlaying']

    def playing(self):
        self.stopTheMusic = False
        # start first track
        self.tracks_number = len(self.playlist)
        NEXT = pygame.USEREVENT + 1
        # get the right speed of each song
        audiofile = TinyTag.get(self.playlist[self.current_track])
        pygame.mixer.init(frequency=audiofile.samplerate)
        print('-------------------------------------------------------------------')
        # sometimes needed I dont know why but on my rasp 4 I dont need this line anymore
        try:
            screen = pygame.display.set_mode((400, 300))
        except Exception as ex:
            print('error but that is fine')

        print('-------------------------------------------------------------------')
        print(self.playlist)
        # start first track
        pygame.mixer.music.load(self.playlist[self.current_track])
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(NEXT)

        self.running = True

        while pygame.mixer.music.get_busy():
           nothing = True

        if self.stopTheMusic == False:
            self.next()




 

