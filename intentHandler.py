#!/usr/bin/env python3
import json, random
import io, configparser
import paho.mqtt.client as mqtt


from services.musicPlayer.musicplayer import MuuzikPlayer
from services.date.date import DateService
from services.wlan.wlan import Wlan
from services.timer.timer import startTimer, timerRemainingTime, deleteAllTimers, deleteOneTimer
from services.volumeControl.volumeControl import VolumeControl


def read_configuration_file():
    try:
        cp = configparser.ConfigParser()
        with io.open("config.ini", encoding="utf-8") as f:
            cp.read_file(f)
        return {section: {option_name: option for option_name, option in cp.items(section)}
                for section in cp.sections()}
    except (IOError, configparser.Error):
        return dict()

config = read_configuration_file()

try:
    mqqt_host = config['secret']['mqqt_host']
    mqqt_port = int(config['secret']['mqqt_port'])
    language = config['activeLanguage']['language']
except KeyError:
    mqqt_host = "localhost"
    mqqt_port = 1883
    language = "en"


getJsonLanguageFile = open( '/home/pi/home/languages/' + language + '.json', )
LANGUAGE = json.load(getJsonLanguageFile)

MODES = {
    "LISTENING": "LISTENING",
    "PLAYINMUSIC": "PLAYINMUSIC",
    "SCANNING": "SCANNING",
}
#Perhaps this is stupid but there must be some way in which one know what is really happening
ACTIVEMODE = "LISTENING"
print(ACTIVEMODE)

music = MuuzikPlayer({'language': LANGUAGE["musicPlayer"]})
dateService = DateService({'language': LANGUAGE["dateService"]})
volumeControle = VolumeControl({'language': LANGUAGE["volumeControl"]})


def on_connect(client, userdata, flags, rc):
    client.subscribe("hermes/intent/#")
    client.subscribe("hermes/asr/#")
    client.subscribe("hermes/nlu/intentNotRecognized")
    print("Connected. Waiting for intents.")


def on_disconnect(client, userdata, flags, rc):
    client.reconnect()


def on_message(client, userdata, msg):
    nlu_payload = json.loads(msg.payload)
    site_id = nlu_payload["siteId"]
    intent = json.loads(msg.payload)
    print('msg.topic', msg.topic)

    ############################################### Date and Time ###############################################

    if msg.topic == "hermes/nlu/intentNotRecognized":
        answer_length = random.randint(0, len(LANGUAGE["intentNotRecognized"]))
        sentence = LANGUAGE["intentNotRecognized"][answer_length]

        print("Recognition failure")

    if msg.topic == "hermes/intent/Date":
        sentence = dateService.whatDayIsIt()

    if msg.topic == "hermes/intent/Time":
        sentence = dateService.whatIsTheTime()

    if msg.topic == 'hermes/intent/whenIsChristmas':
        sentence = dateService.whenIsChristmas()

    ############################################### Volume Controle  ############################################

    if msg.topic == "hermes/asr/startListening":
         volumeControle.muteVolume()

    if msg.topic == "hermes/asr/stopListening":
         volumeControle.unMuteVolume()

    if msg.topic == 'hermes/intent/VolumeControl':
        if (intent["slots"][0]['slotName'] == 'increaseVolume'):
            sentence = volumeControle.increaseVolume()

        if (intent["slots"][0]['slotName'] == 'decreaseVolume'):
            volumeControle.decreaseVolume()

        if (intent["slots"][0]['slotName'] == 'scream'):
            sentence = volumeControle.setVolume(100)

        if (intent["slots"][0]['slotName'] == 'whisper'):
            sentence = volumeControle.setVolume(20)

        if (intent["slots"][0]['slotName'] == 'volume'):
            sentence = volumeControle.setVolume(intent["slots"][0]["value"]["value"])

    ############################################### Music Player  ###############################################

    if msg.topic == 'hermes/intent/Stop':
        music.stop()

    if msg.topic == 'hermes/intent/Next':
        music.next()

    if msg.topic == 'hermes/intent/Previous':
        music.previous()

    if msg.topic == 'hermes/intent/ScanMusic':
        ACTIVEMODE = MODES["SCANNING"]
        sentence = music.scanMusic()
        ACTIVEMODE = MODES["LISTENING"]


    ###############################################    Wifi      ###############################################

    if msg.topic == "hermes/intent/ScanWlan":
        ACTIVEMODE = MODES["SCANNING"]
        wlanService = Wlan()
        print(LANGUAGE["wlan"])
        sentence = wlanService.scan({'language': LANGUAGE["wlan"]})
        print(sentence)
        ACTIVEMODE = MODES["LISTENING"]

    ###############################################    Timer      ###############################################

    if msg.topic == 'hermes/intent/deleteAllTimers':
        intentMessage = {
            'site_id': site_id,
            'session_id': site_id,
            'language': LANGUAGE['timer']
        }
        deleteAllTimers(client, intentMessage)

    if msg.topic == 'hermes/intent/getTimer':
        intentMessage = {
            'site_id': site_id,
            'session_id': site_id,
            'language': LANGUAGE['timer']
        }
        print(intentMessage)
        print(
            '###############################################    Timer      ###############################################')
        timerRemainingTime(client, intentMessage)

    if msg.topic == 'hermes/intent/Timer':
        duration = {
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'seconds': 0
        }
        slotAmount = len(intent["slots"])
        print(intent)
        startAtIndex = 0
        TimerType = LANGUAGE['timer']['timer']

        if (intent["slots"][0]['slotName'] == 'timerType'):
            startAtIndex = 1
            if intent["slots"][0]["value"]["value"] != 'Timer':
                TimerType = intent["slots"][0]["value"]["value"] + LANGUAGE['timer']['timer']

        for i in range(startAtIndex, slotAmount, 2):
            if intent["slots"][i + 1]['slotName'] == 'durationUnit':
                durationUnit =  intent["slots"][i + 1]["value"]["value"]
                if durationUnit == LANGUAGE['timer']['durationUnit']['days'] or durationUnit == LANGUAGE['timer']['durationUnit']['day'] or  durationUnit == LANGUAGE['timer']['durationUnit']['days2']:
                    duration["days"] = intent["slots"][i]["value"]["value"]
                if durationUnit == LANGUAGE['timer']['durationUnit']['hours'] or durationUnit == LANGUAGE['timer']['durationUnit']['hour']:
                    duration["hours"] = intent["slots"][i]["value"]["value"]
                if durationUnit == LANGUAGE['timer']['durationUnit']['minute'] or durationUnit == LANGUAGE['timer']['durationUnit']['minutes']:
                    duration["minutes"] = intent["slots"][i]["value"]["value"]
                if durationUnit == LANGUAGE['timer']['durationUnit']['seconds'] or durationUnit == LANGUAGE['timer']['durationUnit']['second']:
                    duration["seconds"] = intent["slots"][i]["value"]["value"]

        intentMessage = {
            'timer_type': TimerType,
            'site_id': site_id,
            'session_id': site_id,
            'duration': duration,
            'language': LANGUAGE['timer']
        }
        print(intentMessage)
        startTimer(client, intentMessage)


    if msg.topic == 'hermes/intent/deleteOneTimer':
        if (intent["slots"][0]['slotName'] == 'timerType'):
            if intent["slots"][0]["value"]["value"] != 'Timer':
                TimerType = intent["slots"][0]["value"]["value"] + LANGUAGE['timer']['timer']
                intentMessage = {
                    'timer_type': TimerType,
                    'site_id': site_id,
                    'session_id': site_id,
                    'language': LANGUAGE['timer']
                }

                deleteOneTimer(client, intentMessage)


    if msg.topic == 'hermes/intent/PlayMusic':
        intent_message = intent["slots"][0]["value"]["value"]
        music.play(intent_message)
        sentence = LANGUAGE["okay"]


    client.publish("hermes/tts/say", json.dumps({"text": sentence, "siteId": site_id}))


# Create MQTT client and connect to broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(mqqt_host, mqqt_port)
client.loop_forever()
