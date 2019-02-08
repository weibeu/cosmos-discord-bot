import datetime

from abc import ABC, abstractmethod


class ProfileModelsBase(ABC):

    @property
    @abstractmethod
    def _plugin(self):
        raise NotImplementedError

    @staticmethod
    def time_delta(past, extend_hours) -> tuple:
        future = past + datetime.timedelta(hours=extend_hours)
        # noinspection PyTypeChecker
        delta = future - datetime.datetime.now()
        hours, _ = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(_, 60)
        return hours, minutes, seconds
