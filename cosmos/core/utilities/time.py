from dateutil.relativedelta import relativedelta

import re
import time
import arrow

import datetime
import dateutil.parser


TIME_DELTA_REG = re.compile("""(?:(?P<years>[0-9])(?:years?|y))?                   # e.g. 2y
                               (?:(?P<months>[0-9]{1,2})(?:months?|mo))?           # e.g. 2months
                               (?:(?P<weeks>[0-9]{1,4})(?:weeks?|w))?              # e.g. 10w
                               (?:(?P<days>[0-9]{1,5})(?:days?|d))?                # e.g. 14d
                               (?:(?P<hours>[0-9]{1,5})(?:hours?|h))?              # e.g. 12h
                               (?:(?P<minutes>[0-9]{1,5})(?:minutes?|mins?|m))?    # e.g. 10m
                               (?:(?P<seconds>[0-9]{1,5})(?:seconds?|s))?          # e.g. 15s
                            """, re.VERBOSE)


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


class HumanDateTimeMixin(object):

    def __init__(self, datetime_, message):
        self.datetime = datetime_
        self.message = message
        self.arrow = arrow.get(self.datetime)

    @staticmethod
    def __get_normalized_message(*tokens):
        message = tokens[-1] if tokens else str()
        to_normalize = " "
        if message.startswith(to_normalize):
            message = message.strip(to_normalize)
        return message

    @classmethod
    def from_human(cls, string):
        datetime_, tokens = parse_human_datetime(string)
        message = cls.__get_normalized_message(*tokens)
        return cls(datetime_, message)

    @classmethod
    def from_human_timedelta(cls, string):
        datetime_, message = parse_human_timedelta(string)
        message = cls.__get_normalized_message(message)
        return cls(datetime_, message)

    @property
    def humanize(self):
        return self.arrow.humanize()

    @property
    def delta(self):
        return self.datetime - datetime.datetime.utcnow()


def parse_human_timedelta(string):
    match = TIME_DELTA_REG.match(string)
    if not (match and match.group(0)):
        raise ValueError

    datetime_ = datetime.datetime.utcnow()

    # TODO: Ignore 'and' in between deltas.

    def __parse_remaining(s, dt=datetime_):
        m = TIME_DELTA_REG.match(s)
        if not (m and m.group(0)):
            return dt, s
        # noinspection PyTypeChecker
        data = {k: int(v) for k, v in m.groupdict(default=0).items()}
        remaining = s[m.end():].strip()
        dt = dt + relativedelta(**data)
        return __parse_remaining(remaining, dt)

    return __parse_remaining(string)


def parse_human_datetime(string):
    try:
        return dateutil.parser.parse(string, fuzzy_with_tokens=True)
    except (TypeError, Exception):
        raise ValueError
