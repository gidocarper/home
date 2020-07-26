#!/usr/bin/python
# -*- coding: utf-8 -*-
import io, configparser
import paho.mqtt.client as mqtt

#from translate import Translator
from translate import Translator



def read_configuration_file():
    try:
        cp = configparser.ConfigParser()
        with io.open("../config.ini", encoding="utf-8") as f:
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


def on_message(client, userdata, message):
    translate = Translator()
    msg = str(message.payload.decode("utf-8"))
    print('msg', msg)
    translate.init(msg)


def on_connect(client, userdata, flags, rc):
    client.subscribe('/home/translate')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqqt_host)

print("Connected to MQTT Broker: " + mqqt_host)

client.loop_forever()