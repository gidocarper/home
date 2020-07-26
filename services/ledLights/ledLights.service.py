#!/usr/bin/env python3
import json
import time
from pixels import Pixels, pixels
from alexa_led_pattern import AlexaLedPattern
from google_home_led_pattern import GoogleHomeLedPattern
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    client.subscribe("hermes/tts/say")
    client.subscribe("hermes/asr/#")
    client.subscribe("hermes/audioServer/default/playFinished")



def on_disconnect(client, userdata, flags, rc):
    client.reconnect()

def on_message(client, userdata, msg):
    if msg.topic == "hermes/asr/startListening":
        pixels.think()

    if msg.topic == "hermes/audioServer/default/playFinished":
        pixels.off()

    if msg.topic == "hermes/asr/stopListening":
        pixels.off()

    if msg.topic == "hermes/tts/say":
        pixels.speak()
    #client.publish("hermes/tts/say", json.dumps({"text": sentence}))

pixels.pattern = AlexaLedPattern(show=pixels.show)
# Create MQTT client and connect to broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect("localhost", 1883)
client.loop_forever()

