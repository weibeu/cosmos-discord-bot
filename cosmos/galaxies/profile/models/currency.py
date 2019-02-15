import arrow
import asyncio
import random

from abc import ABC
from .base import ProfileModelsBase


class Boson(ProfileModelsBase, ABC):

    def __init__(self, **kwargs):
        raw_currency = kwargs.get("currency", dict())
        self._bosons = raw_currency.get("bosons", 0)
        self.boson_daily_datetime = raw_currency.get("daily_datetime")

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

    @property
    def can_take_daily_bosons(self):
        if not self.boson_daily_datetime:
            return True
        delta = arrow.utcnow() - self.boson_daily_datetime
        return delta.seconds >= self._plugin.data.boson.daily_cooldown*60*60

    @property
    def daily_bosons_delta(self) -> tuple:
        return self.time_delta(self.boson_daily_datetime, self._plugin.data.boson.daily_cooldown)

    async def take_daily_bosons(self, target_profile=None):
        profile = target_profile or self
        profile._bosons += self._plugin.data.boson.default_daily
        self.boson_daily_datetime = arrow.utcnow()
        await self._collection.update_one(
            {"user_id": self.id}, {"$set": {"currency.daily_datetime": self.boson_daily_datetime.datetime}}
        )


class Fermion(ProfileModelsBase, ABC):

    def __init__(self, **kwargs):
        raw_currency = kwargs.get("currency")
        self._fermions = raw_currency.get("fermions", 0)

    @property
    def fermions(self):
        return self._fermions

    async def give_fermions(self, fermions: int):
        self._fermions += fermions

        await self._collection.update_one(
            {"user_id": self.id}, {"$set": {"currency.fermions": self.fermions}}
        )
