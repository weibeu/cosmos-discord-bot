import datetime


class Time(object):

    def __init__(self):
        self.microsecond = 0
        self.second = 0
        self.minute = 0
        self.hour = 0
        self.date = 0
        self.month = 0
        self.year = 0

    def now(self):
        now = datetime.datetime.now()
        self.microsecond = now.microsecond
        self.second = now.second
        self.minute = now.minute
        self.hour = now.hour
        self.date = now.day
        self.month = now.month
        self.year = now.year
        return self
