"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from abc import ABC, abstractmethod

import arrow
import datetime


class ProfileModelsBase(ABC):

    @property
    def _cache_permanent_persist_(self):
        return self.is_prime

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
