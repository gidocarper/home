#!/usr/bin/env python3 -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import configparser
import time, io
import picamera
import datetime
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def read_configuration_file(self):
    try:
        cp = configparser.ConfigParser()
        with io.open("config.ini", encoding="utf-8") as f:
            cp.read_file(f)
        return {section: {option_name: option for option_name, option in cp.items(section)}
                for section in cp.sections()}
    except (IOError, configparser.Error):
        return dict()


Subject = 'Achtung!'
subject = 'Motion Detected'


def getFileName():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

# sensor setup

sensorPin = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

prevState = False
currState = False

camera = picamera.PiCamera()

while True:
    time.sleep(0.1)
    prevState = currState
    currState = GPIO.input(sensorPin)
    if currState != prevState:
        newState = "HIGH" if currState else "LOW"
        print ("GPIO pin %s is %s" % (sensorPin, newState))
        time.sleep(2)
        camera.capture('movement.jpg')
        time.sleep(10)

        subject = 'Security allert!!'

        fp = open('movement.jpg', 'rb')
        fp.close()

        print('movement !!!')

        #server = smtplib.SMTP(smtpServer, 587)
        #server.starttls()
        #server.login(user='info@kujaja.com', password='Ashakan!29')
        #server.send_message(msg)
        #server.quit()
