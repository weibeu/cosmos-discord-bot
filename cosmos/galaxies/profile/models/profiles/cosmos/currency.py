import math
import arrow
import asyncio
import random

from abc import ABC

from ..base import ProfileModelsBase


class Boson(ProfileModelsBase, ABC):

    __STREAK_MULTIPLIER = 7

    def __init__(self, **kwargs):
        raw_currency = kwargs.get("currency", dict())
        self._bosons = raw_currency.get("bosons", 0)
        self.boson_daily_streak = raw_currency.get("bosons_daily_streak", 0)
        self.boson_daily_timestamp = self.get_arrow(raw_currency.get("boson_daily_timestamp"))

        self.in_boson_buffer = False

    @property
    def bosons(self):
        return self._bosons

    def give_bosons(self, bosons: int):
        if self.bosons + bosons > self.plugin.data.boson.max_limit:
            raise OverflowError

        self._bosons += int(bosons)

    async def give_default_bosons(self):
        bosons = random.randint(self.plugin.data.boson.default_min, self.plugin.data.boson.default_max)

        try:
            self.give_bosons(bosons)
        except OverflowError:
            return

        self.in_boson_buffer = True
        await asyncio.sleep(self.plugin.data.boson.buffer_cooldown)
        self.in_boson_buffer = False

    @property
    def can_take_daily_bosons(self):
        if not self.boson_daily_timestamp:
            return True
        return arrow.utcnow() > self.next_daily_bosons

    @property
    def on_bosons_daily_streak(self):
        streak_buffer = self.get_future_arrow(self.boson_daily_timestamp, hours=self.plugin.data.boson.streak_buffer)
        if arrow.utcnow() > streak_buffer:
            return False
        return True

    @property
    def next_daily_bosons(self):
        return self.get_future_arrow(self.boson_daily_timestamp, hours=self.plugin.data.boson.daily_cooldown)

    async def take_daily_bosons(self, target_profile=None):
        profile = target_profile or self

        bonus = self.plugin.data.boson.target_bonus if self.id != target_profile.id else 0

        bosons = self.plugin.data.boson.default_daily + bonus

        if self.on_bosons_daily_streak:
            self.boson_daily_streak += 1
            bosons += round(math.log(self.boson_daily_streak) ** math.sqrt(self.__STREAK_MULTIPLIER))
        else:
            self.boson_daily_streak = 0

        profile.give_bosons(bosons)
        self.boson_daily_timestamp = arrow.utcnow()

        await self.collection.update_one(self.document_filter, {"$set": {
            "currency.boson_daily_timestamp": self.boson_daily_timestamp.datetime,
            "currency.bosons_daily_streak": self.boson_daily_streak,
        }})

        return bosons, bonus


class Fermion(ProfileModelsBase, ABC):

    def __init__(self, **kwargs):
        raw_currency = kwargs.get("currency", dict())
        self._fermions = raw_currency.get("fermions", 0)

    @property
    def fermions(self):
        return self._fermions

    async def give_fermions(self, fermions: int):
        self._fermions += fermions

        await self.collection.update_one(
            self.document_filter, {"$set": {"currency.fermions": self.fermions}}
        )
