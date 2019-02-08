import asyncio
import random

from abc import ABC
from .base import ProfileModelsBase


class Boson(ProfileModelsBase, ABC):

    def __init__(self, **kwargs):
        raw_currency = kwargs.get("currency", dict())
        self._bosons = raw_currency.get("bosons", 0)
        self.in_boson_buffer = False

    @property
    def bosons(self):
        return self._bosons

    def give_bosons(self, bosons: int):
        self._bosons += int(bosons)

    async def give_default_bosons(self):
        bosons = random.randint(self._plugin.data.boson.default_min, self._plugin.data.boson.default_max)
        self.give_bosons(bosons)

        self.in_boson_buffer = True
        await asyncio.sleep(self._plugin.data.boson.buffer_cooldown)
        self.in_boson_buffer = False
