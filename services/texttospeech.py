#!/usr/bin/env python3 -*- coding: utf-8 -*-

import requests, json, base64
import random
import io
import configparser
import time
from os import path
from slugify import slugify
import paho.mqtt.client as mqtt
import pygame

NEXT = pygame.USEREVENT + 1
#os.environ["SDL_VIDEODRIVER"] = "dummy"

class TextToSpeech:
    def read_configuration_file(self):
        try:
            cp = configparser.ConfigParser()
            with io.open("../config.ini", encoding="utf-8") as f:
                cp.read_file(f)
            return {section: {option_name: option for option_name, option in cp.items(section)}
                    for section in cp.sections()}
        except (IOError, configparser.Error):
            return dict()


    def __init__(self):
        config = self.read_configuration_file()
        # self.text_to_translate = None
        # self.language = None
        self.language = 'fr'
        self.country = 'FR'

        try:
            self.azure_translate_key = config['secret']['azure_key']
        except KeyError:
            self.azure_translate_key = "XXXXXXXXXXXXXXXXXXXXX"
        try:
            self.google_wavenet_key = config['secret']['google_wavenet_key']
        except KeyError:
            self.google_wavenet_key = "XXXXXXXXXXXXXXXXXXXXX"
        try:
            self.translator_voice_gender = config['secret']['translator_voice_gender']
        except KeyError:
            self.translator_voice_gender = "FEMALE"


    def lights(self, typeOfLight):
        client = mqtt.Client()
        client.connect("jimmy", 1883, 60)
        client.publish("/home/led", typeOfLight)
        client.disconnect()


    def speak(self, translation, language, country):
        self.lights('think')

        translation = bytes(translation, "utf-8").decode("unicode_escape")
        fileName = '/home/pi/voices/' + language + '-' + self.translator_voice_gender + '-' + slugify(translation) + '.mp3'
        #print(fileName)
        self.lights('speak')
        if not path.exists(fileName):
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }

            data = u'{\'input\':{\'text\':\'' + translation + '.\'},\'voice\':{\'languageCode\':\'' + language + '-' + language + '\',\'name\':\'' + language + '-' + country + '-Wavenet-A\',\'ssmlGender\':\'' + self.translator_voice_gender + '\'},\'audioConfig\':{\'audioEncoding\':\'MP3\'}}'
            #print(data);
            response = requests.post('https://texttospeech.googleapis.com/v1/text:synthesize?key=' + self.google_wavenet_key, headers=headers, data=data)
            file_content = base64.b64decode(json.loads(response.text)['audioContent'])
            filemp3 = open(fileName, "wb")
            filemp3.write(file_content)
            filemp3.close()

        #screen = pygame.display.set_mode((1024, 768))
        pygame.mixer.init(frequency=48000)
        pygame.mixer.music.load(fileName)
        pygame.mixer.music.set_volume(5.0)
        pygame.mixer.music.play()
        time.sleep(3)
        self.lights('stop')


    def get_language_code(self):
        switcher = {
            'Australisch': 'en',
            'Amerikanisch': 'en',
            'Belgisch': 'be',
            'Britisch': 'en',
            'Dänisch': 'da',
            'Französisch': 'fr',
            'Englisch': 'en',
            'Italienisch': 'it',
            'Japanisch': 'ja',
            'Koreanisch': 'ko',
            'Niederländisch': 'nl',
            'Norwegisch': 'nb',
            'Brasilianisch': 'pt',
            'Portugiesisch': 'pt',
            'Polnisch': 'pl',
            'Russisch': 'ru',
            'Slowakisch': 'sk',
            'Schwedisch': 'sv',
            'Spanisch': 'es',
            'Türkisch': 'tr',
            'Ukrainisch': 'uk'
        }
        return switcher.get(self.language, "fr")


    def get_country_code(self):
        switcher = {
            'Australisch': 'AU',
            'Amerikanisch': 'US',
            'Belgisch': 'BE',
            'Britisch': 'GB',
            'Dänisch': 'DK',
            'Englisch': 'GB',
            'Französisch': 'FR',
            'Italienisch ': 'IT',
            'Japanisch': 'JP',
            'Koreanisch': 'KR',
            'Niederländisch': 'NL',
            'Norwegisch': 'NO',
            'Brasilianisch': 'BR',
            'Portugiesisch': 'PT',
            'Polnisch': 'PL',
            'Russisch': 'RU',
            'Slowakisch': 'SK',
            'Schwedisch': 'SE',
            'Spanisch': 'ES',
            'Türkisch': 'TR',
            'Ukrainisch': 'UA'
        }
        return switcher.get(self.language, "fr")


    def error_response(self, data):
        response = random.choice(["Es ist leider kein Internet verfügbar.",
                                  "Ich bin nicht mit dem Internet verbunden.",
                                  "Es ist kein Internet vorhanden.",
                                  "Leider ist ein Fehler aufgetreten"])

        return response


