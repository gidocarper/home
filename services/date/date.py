#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import datetime

class DateService:
    def __init__(self, intentMessage):
        self.language = intentMessage["language"]
        return

    def whatDayIsIt(self):
        print('2')
        now = datetime.datetime.now()
        print(now)
        print(self.language["whatDayIsIt"])
        print(now.strftime("%d/%m/%Y"))
        return  self.language["whatDayIsIt"].format(now.strftime("%d/%m/%Y"))

    def whatIsTheTime(self):
        # datetime object containing current date and time
        now = datetime.datetime.now()
        return  self.language["whatIsTheTime"].format(now.strftime("%H:%M:%S"))

    def whenIsChristmas(self):
        today = datetime.datetime.now()
        christmas = datetime.datetime(today.year, 12, 25)
        if (today >= christmas):
            christmas = datetime.datetime(today.year + 1, 12, 25)
        days = (christmas - today).days
        print(self.language["whenIsChristmas"].format(days))
        return self.language["whenIsChristmas"].format(days)
