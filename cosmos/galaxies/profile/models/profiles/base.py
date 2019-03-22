import datetime

from abc import ABC, abstractmethod

import arrow


class ProfileModelsBase(ABC):

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
