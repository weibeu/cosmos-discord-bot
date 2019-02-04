import math

from abc import ABC, abstractmethod
from .base import ProfileModelsBase


class UserLevel(ProfileModelsBase, ABC):

    K = 1

    @property
    @abstractmethod
    def xp(self):
        raise NotImplementedError

    def from_xp(self):
        return math.floor(math.log(self.xp*math.e + math.e))*self.K

    @property
    def level(self):
        return self.from_xp()
