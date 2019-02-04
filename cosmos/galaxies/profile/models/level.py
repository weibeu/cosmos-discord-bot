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
        return (self._xp_level + math.log(self._level + math.e))*self.K

    @property
    def delta_xp(self):
        # Basically property for public use.
        return int(self.__delta_xp - self.xp)

    def from_delta_xp(self):
        # return math.floor(math.log(self.xp/(math.log(math.exp(self.xp)) + math.e) + math.e))*self.K
        # return math.floor(math.log(self.xp / math.log(self.xp + 2) + math.e)) * self.K
        while self.delta_xp <= self.xp:
            self._xp_level += self.__delta_xp
            self._level += 1
        return self._level

    @property
    def level(self):
        return self.from_delta_xp()
