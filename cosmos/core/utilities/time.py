import datetime
import time


class Time(object):

    def __init__(self):
        self.init_time = time.time()
        self.cosmos_time = 0   # Cosmos time
        self.microsecond = 0
        self.second = 0
        self.minute = 0
        self.hour = 0
        self.date = 0
        self.month = 0
        self.year = 0

    def now(self):
        now = datetime.datetime.now()
        self.cosmos_time = time.time() - self.init_time
        self.microsecond = now.microsecond
        self.second = now.second
        self.minute = now.minute
        self.hour = now.hour
        self.date = now.day
        self.month = now.month
        self.year = now.year
        return self

    @staticmethod
    def calc_time(decorated):

        def wrapper(*args, **kwargs):
            start_time = time.time()
            var = decorated(*args, **kwargs)
            if hasattr(args[0], 'log') and args[0].log:
                log = args[0].log
                log.info(f"Done. [{round(time.time() - start_time, 3)}s].\n\n")
            else:
                print(f"Done. [{round(time.time() - start_time, 3)}s].\n\n")
            return var
        return wrapper

    def time(self):
        return time.time() - self.init_time

    def round_time(self):
        return round(self.time(), 3)
