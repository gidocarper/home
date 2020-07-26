#!/usr/bin/python
# -*- coding: utf-8 -*-
import time, io, configparser
import paho.mqtt.client as mqtt



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
except KeyError:
    mqqt_host = "localhost"


def callService(typeOfService, message):
    client = mqtt.Client()
    client.connect(mqqt_host, 1883, 60)
    client.publish('/home/' + typeOfService , message)
    client.disconnect()

def on_message(client, userdata, message):
    print("message received: ", message)
    print('client', client)
    print('userdata', userdata)
    print("message topic: ", message.topic)
    print('message', message.payload)

    msg = str(message.payload.decode("utf-8"))
    if 'musik' in msg:
        mainAction = 'music'
        callService(mainAction, msg)
        print('musik spielen')

    if 'übersetzen' in msg:
        mainAction = 'translate'
        print('translate')
        callService(mainAction, msg)


def on_connect(client, userdata, flags, rc):
    client.subscribe('/home/message')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqqt_host)

print("Connected to MQTT Broker: " + mqqt_host)

client.loop_forever()