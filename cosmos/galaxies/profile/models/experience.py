from abc import ABC

from cosmos.galaxies.profile.models.base import ProfileModelsBase


class UserExperience(ProfileModelsBase, ABC):

    def __init__(self, xp: int):
        self._xp = xp

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, xp: int):
        self._xp = int(xp)

    def give_xp(self, xp):
        self._xp += xp
