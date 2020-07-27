#!/usr/bin/env python3
import json
from datetime import timedelta
from threading import Thread
from subprocess import call
import time


TIMER_LIST = []
TIMER_LIST_EXT = []


class TimerBase(Thread):
    """
    """
    def __init__(self, hermes, intentMessage):
        super(TimerBase, self).__init__()
        self._start_time = 0
        self.hermes = hermes
        self.session_id = intentMessage["session_id"]
        self.site_id = intentMessage["site_id"]
        self.sentence = None
        self.timerType = intentMessage["timer_type"]
        self.duration = intentMessage["duration"]
        self.LANGUAGE = intentMessage["language"]
        self.durationRaw = self.get_duration_raw(self.duration, intentMessage)
        self.wait_seconds = self.get_seconds_from_duration(self.duration)

        TIMER_LIST.append(self)
        TIMER_LIST_EXT.append({
            'timer_type': intentMessage["timer_type"],
            'wait_seconds': self.wait_seconds,
            'start_time': time.time()
        })
        self.send_end()

    @staticmethod
    def get_seconds_from_duration(duration):
        days = duration["days"]
        hours = duration["hours"]
        minutes = duration["minutes"]
        seconds = duration["seconds"]
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds).total_seconds()

    @staticmethod
    def get_duration_raw(duration, intentMessage):
        result = ''
        days = duration["days"]
        hours = duration["hours"]
        minutes = duration["minutes"]
        seconds = duration["seconds"]

        length = 0

        if seconds > 0:
            result = intentMessage["language"]["timerBase"]["get_duration_raw"]["seconds"].format(str(seconds))

            length += 1
        if minutes > 0:
            if length > 0:
                add_and = intentMessage["language"]["timerBase"]["get_duration_raw"]["and"]
            else:
                add_and = ''
            result = intentMessage["language"]["timerBase"]["get_duration_raw"]["minutes"].format(str(minutes), add_and, result)
            length += 1
        if hours > 0:
            if length > 1:
                add_and = ', '
            elif length > 0:
                add_and = intentMessage["language"]["timerBase"]["get_duration_raw"]["and"]
            else:
                add_and = ''
            result = intentMessage["language"]["timerBase"]["get_duration_raw"]["hours"].format(str(hours), add_and, result)
            length += 1
        if days > 0:
            if length > 1:
                add_and = ', '
            elif length > 0:
                add_and = intentMessage["language"]["timerBase"]["get_duration_raw"]["and"]
            else:
                add_and = ''
            result = intentMessage["language"]["timerBase"]["get_duration_raw"]["days"].format(str(days), add_and, result)
        return result


    def run(self):
        # print("[{}] Start teimer: wait {} seconds".format(time.time(), self.wait_seconds))
        self._start_time = time.time()
        time.sleep(self.wait_seconds)
        self.__callback()

    def __callback(self):
        # print("[{}] End timer: wait {} seconds".format(time.time(), self.wait_seconds))
        TIMER_LIST.remove(self)
        self.callback()

    def callback(self):
        raise NotImplementedError('You should implement your callback')

    def send_end(self):
        raise NotImplementedError('You should implement your send end')


class TimerSendNotification(TimerBase):

    def callback(self):
        if self.sentence is None:
            text = self.LANGUAGE["timerSendNotification"]["callback"]["timerWithName"].format(str(self.durationRaw), str(self.timerType))
        else:
            text = self.LANGUAGE["timerSendNotification"]["callback"]["timerWithOutName"].format(
                self.durationRaw, self.timerType, self.sentence)
        call(["aplay", "-q", "/home/pi/home/services/timer/Gentle-wake-alarm-clock.wav"])
        self.hermes.publish("hermes/tts/say", json.dumps({"text": text, "siteId": self.site_id}))

    def send_end(self):
        if self.sentence is None:
            text = self.LANGUAGE["timerSendNotification"]["send_end"]["timerWithName"].format(str(self.durationRaw),str(self.timerType))
        else:
            text = self.LANGUAGE["timerSendNotification"]["send_end"]["timerWithOutName"].format(str(self.durationRaw), str(self.timerType), str(self.sentence))

        self.hermes.publish("hermes/tts/say", json.dumps({"text": text, "siteId": self.site_id}))


def getPronounceableTime(timeInSeconds, intentMessage):
    seconds = timeInSeconds
    if seconds == 0:
        return intentMessage['language']["get_duration_raw"]["null"]

    result = ''
    add_and = ''
    t = str(timedelta(seconds=seconds)).split(':')

    if int(t[2]) > 0:
        add_and = intentMessage['language']["get_duration_raw"]["and"]
        result += intentMessage['language']["get_duration_raw"]["seconds"].format(int(t[2]))


    if int(t[1]) > 0:
        result = intentMessage['language']["get_duration_raw"]["minutes"].format(int(t[1]), add_and, result)
        if add_and != '':
            add_and = ', '
        else:
            add_and = intentMessage['language']["get_duration_raw"]["and"]

    if int(t[0]) > 0:
        result = intentMessage['language']["get_duration_raw"]["hours"].format(int(t[0]), add_and, result)
    #TODO Add days
    return result


def startTimer(hermes, intentMessage):
    timer = TimerSendNotification(hermes, intentMessage)
    timer.start()
    return timer


def timerRemainingTime(hermes, intentMessage):
    len_timer_list = len(TIMER_LIST)
    text =  intentMessage['language']['timerRemainingTime']['amountOfTimers'].format(str(len_timer_list))
    if len_timer_list == 1:
        text = intentMessage['language']['timerRemainingTime']['oneTimer']
    counter = 0
    if len_timer_list < 1:
        hermes.publish("hermes/tts/say", json.dumps({"text": intentMessage['language']['timerRemainingTime']['noTimer'], "siteId": intentMessage["site_id"]}))
    else:
        for timers in TIMER_LIST_EXT:
            timeLeft = getPronounceableTime(int((timers['start_time'] + timers['wait_seconds']) - time.time()), intentMessage)
            AmountOfTimer = getFirstSecondTimer(counter + 1, intentMessage)
            if (timers['timer_type'] != intentMessage['language']["timer"]):
                AmountOfTimer = ''
            text += intentMessage['language']['timerRemainingTime']['multipleTimerTypes'].format(AmountOfTimer, timers['timer_type'], timeLeft)
            counter = counter + 1
        hermes.publish("hermes/tts/say", json.dumps({"text": text, "siteId": intentMessage["site_id"]}))


def getFirstSecondTimer(i, intentMessage):
    switcher={
            1:intentMessage["language"]["getFirstSecondTimer"]["first"],
            2: intentMessage["language"]["getFirstSecondTimer"]["second"],
            3: intentMessage["language"]["getFirstSecondTimer"]["third"],
            4: intentMessage["language"]["getFirstSecondTimer"]["fourth"],
            5: intentMessage["language"]["getFirstSecondTimer"]["fifth"]
         }
    return switcher.get(i,"weiter")


def deleteOneTimer(hermes, intentMessage):
    len_timer_list = len(TIMER_LIST)
    text = None
    if len_timer_list == 1:
        TIMER_LIST.clear()
        TIMER_LIST_EXT.clear()
        text = intentMessage["language"]["deleteOneTimer"].format(intentMessage['timer_type'])

    counter = 0
    if len_timer_list > 1:
        for timers in TIMER_LIST_EXT:
            if (timers['timer_type'] == intentMessage['timer_type']):
                TIMER_LIST.pop(counter)
                TIMER_LIST_EXT.pop(counter)
                text = intentMessage["language"]["deleteOneTimer"].format( timers['timer_type'])
            counter = counter + 1

    if text:
        hermes.publish("hermes/tts/say", json.dumps({"text": text, "siteId": intentMessage["site_id"]}))

def deleteAllTimers(hermes, intentMessage):
    TIMER_LIST.clear()
    TIMER_LIST_EXT.clear()
    hermes.publish("hermes/tts/say", json.dumps({"text": intentMessage['language']["deleteAllTimers"], "siteId": intentMessage["site_id"]}))

