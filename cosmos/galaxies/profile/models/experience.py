from abc import ABC

from cosmos.galaxies.profile.models.base import ProfileModelsBase


class UserExperience(ProfileModelsBase, ABC):

    def __init__(self, xp: int):
        self._xp = xp

    @property
    def xp(self):
        return self._xp
