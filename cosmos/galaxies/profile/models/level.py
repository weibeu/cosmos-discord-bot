import math

from abc import ABC, abstractmethod
from .base import ProfileModelsBase


class UserLevel(ProfileModelsBase, ABC):

    K = 100

    def __init__(self, _level: int):
        self._level = _level
        self._xp_level = 0

    @property
    @abstractmethod
    def xp(self):
        raise NotImplementedError

    @property
    def xp_level(self):
        return self._xp_level + self.__delta_xp

    @property
    def __delta_xp(self):
        return math.log(self._level + math.e)*self.K

    @property
    def delta_xp(self):
        return int(self.xp_level - self.xp)

    def from_delta_xp(self):
        while self.delta_xp <= self.xp:
            self._xp_level += self.__delta_xp
            self._level += 1    # Don't really need self._level -= 1 'cause user will never loose xp.
        return self._level

    @property
    def level(self):
        return self.from_delta_xp()
