from abc import ABC

from cosmos.galaxies.profile.models.base import ProfileModelsBase


class CosmosCurrency(ProfileModelsBase, ABC):

    def __init__(self, value: int):
        self._currency = value

    @property
    def currency(self):
        return self._currency
