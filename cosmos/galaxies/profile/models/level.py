from abc import ABC

from .base import ProfileModelsBase


class UserLevel(ProfileModelsBase, ABC):

    def __init__(self):
        pass

    @property
    def level(self):
        return
