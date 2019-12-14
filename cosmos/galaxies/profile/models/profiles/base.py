import datetime

from abc import ABC, abstractmethod

import arrow


class ProfileModelsBase(ABC):

    @property
    def name(self):
        return self.user.name

    @property
    @abstractmethod
    def plugin(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def collection(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    def user(self):
        return self.plugin.bot.get_user(self.id)

    @property
    @abstractmethod
    def is_prime(self):
        raise NotImplementedError

    @staticmethod
    def get_arrow(timestamp):
        if timestamp:
            return arrow.get(timestamp)

    @staticmethod
    def get_future_arrow(past, **kwargs):
        return arrow.get(past) + datetime.timedelta(**kwargs)

    @property
    def document_filter(self):
        return {
            "user_id": self.id
        }
