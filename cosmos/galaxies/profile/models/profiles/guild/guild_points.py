import asyncio
import random
from abc import ABC

import math
import arrow

from .base import GuildMemberProfileBase


class GuildPoints(GuildMemberProfileBase, ABC):

    __STREAK_MULTIPLIER = 10

    def __init__(self, **kwargs):
        raw_points = kwargs.get("points", dict())
        self.points = raw_points.get("points", 0)
        self.points_daily_streak = raw_points.get("daily_streak", 0)
        self.points_daily_timestamp = raw_points.get("daily_timestamp")

        self.in_points_buffer = False

    def give_points(self, points: int):
        if self.points + points > self.plugin.data.points.max_limit:
            raise OverflowError

        self.points += points

    async def give_default_points(self):
        points = random.randint(self.plugin.data.points.default_min, self.plugin.data.points.default_max)

        try:
            self.give_points(points)
        except OverflowError:
            return

        self.in_points_buffer = True
        await asyncio.sleep(self.plugin.data.points.buffer_cooldown)
        self.in_points_buffer = False

    @property
    def on_points_daily_streak(self):
        streak_buffer = self.get_future_arrow(self.points_daily_timestamp, hours=self.plugin.data.points.streak_buffer)
        if arrow.utcnow() > streak_buffer:
            return False
        return True

    @property
    def next_daily_points(self):
        return self.get_future_arrow(self.points_daily_timestamp, hours=self.plugin.data.points.daily_cooldown)

    @property
    def can_take_daily_points(self):
        if not self.points_daily_timestamp:
            return True
        return arrow.utcnow() > self.next_daily_points

    async def take_daily_points(self, target_profile=None):
        profile = target_profile or self

        bonus = self.plugin.data.points.target_bonus if self.id != target_profile.id else 0

        points = self.plugin.data.points.default_daily + bonus

        if self.on_points_daily_streak:
            self.points_daily_streak += 1
            points += round(math.log(self.points_daily_streak) ** math.sqrt(self.__STREAK_MULTIPLIER))
        else:
            self.points_daily_streak = 0

        profile.give_points(points)
        self.points_daily_timestamp = arrow.utcnow()

        await self.collection.update_one(self.document_filter, {"$set": {
            f"{self.guild_filter}.points.daily_timestamp": self.points_daily_timestamp.datetime,
            f"{self.guild_filter}.points.daily_streak": self.points_daily_streak,
        }})
        return points, bonus
