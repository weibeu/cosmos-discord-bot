from abc import ABC

from cosmos.galaxies.profile.models.base import ProfileModelsBase


class UserExperience(ProfileModelsBase, ABC):

    def __init__(self):
        pass

    @property
    def xp(self):
        return
