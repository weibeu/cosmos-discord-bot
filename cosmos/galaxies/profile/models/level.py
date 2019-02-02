from abc import ABC, abstractmethod

from .base import ProfileModelsBase


class UserLevel(ProfileModelsBase, ABC):

    @property
    @abstractmethod
    def xp(self):
        raise NotImplementedError

    def from_xp(self):
        return int(self.xp / 10)

    @property
    def level(self):
        return self.from_xp()
