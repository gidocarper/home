# !/usr/bin/python3
# -*- coding: utf-8 -*-


import requests, json
import paho.mqtt.client as mqtt

from texttospeech import TextToSpeech

textToSpeech = TextToSpeech()
translateFrom = 'en'
translateInto = 'fr'
translateIntoCountry = 'fr'

class Translator:
    def __init__(self):
        self.textToSpeech = textToSpeech
        #translateInto = 'fr'
        #translateIntoCountry = 'fr'

    def init(self, res):
        global translateFrom
        global translateInto
        global translateIntoCountry
        print('Translator init', res)
        print(res)
        if res in 'french' or res in 'französisch':
            translateInto = 'fr'
            translateIntoCountry = 'FR'
        elif res in 'dutch' or res in 'niederländisch':
            translateInto = 'nl'
            translateIntoCountry = 'NL'
        elif res in 'english' or res in 'englisch':
            translateInto = 'en'
            translateIntoCountry = 'GB'
        elif res in 'german' or res in 'deutsch':
            translateInto = 'de'
            translateIntoCountry = 'DE'
        elif res in 'russian' or res in 'russisch':
            print('russian is set')
            translateInto = 'ru'
            translateIntoCountry = 'RU'

        print('translateInto', translateInto)
        print('translateFrom', translateFrom)

        print('translateIntoCountry', translateIntoCountry)

        textToTranslate = res.replace(r"'", r"\'")
        if textToTranslate != '':
            translation = self.translate(textToTranslate, translateFrom, translateInto,
                                         self.textToSpeech.azure_translate_key)
            print(translation)
            if translation != '':
                self.textToSpeech.speak(self.cleanMicroSoftTranslation(translation), translateInto, translateIntoCountry)


    def cleanMicroSoftTranslation(self, text):
        # this sucks has anybody a better idea?
        return text.replace('<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">', '').replace(
            '</string>',
            '').replace(
            '<Response [200]>', '').replace(r"'", r"\'")

    def translate(self, text, fromLanguage, toLanguage, azure_translate_key):
        body = [{'text': str(text)}]

        token_url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
        token_body = json.dumps('{body}')
        token_headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(token_body)),
            'Ocp-Apim-Subscription-Key': azure_translate_key
        }
        request = requests.post(token_url, headers=token_headers, json=token_body)

        accessToken = (request.content).decode('utf-8')

        params = u'text={}&to={}&from={}&appId=Bearer+{}'.format(str(text), str(toLanguage),
                                                                 str(fromLanguage),
                                                                 str(accessToken))
        translateUrl = u'http://api.microsofttranslator.com/v2/Http.svc/Translate?{}'.format(str(params))

        headers = {
            'Content-type': 'application/json'
        }
        request = requests.get(translateUrl, headers=headers, json=body)

        rawTranslation = request.text
        return self.cleanMicroSoftTranslation(rawTranslation)


#if __name__ == "__main__":
    # initialize speech
#    Translator()
