from abc import ABC

from .base import ProfileModelsBase


class Boson(ProfileModelsBase, ABC):

    def __init__(self, bosons: int):
        self._bosons = bosons

    @property
    def bosons(self):
        return self._bosons
