import asyncio
import random
from abc import ABC

import arrow

from .base import GuildMemberProfileBase


class GuildPoints(GuildMemberProfileBase, ABC):

    def __init__(self, **kwargs):
        raw_points = kwargs.get("points", dict())
        self.points = raw_points.get("points", 0)
        self.points_daily_timestamp = raw_points.get("daily_timestamp")

        self.in_points_buffer = False

    def give_points(self, points: int):
        self.points += points

    async def give_default_points(self):
        points = random.randint(self.plugin.data.points.default_min, self.plugin.data.points.default_max)
        self.give_points(points)

        self.in_points_buffer = True
        await asyncio.sleep(self.plugin.data.points.buffer_cooldown)
        self.in_points_buffer = False

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
        profile.points += self.plugin.data.points.default_daily
        self.points_daily_timestamp = arrow.utcnow()
        await self.collection.update_one(
            self.document_filter,
            {"$set": {f"{self.guild_filter}.points.daily_timestamp": self.points_daily_timestamp.datetime}}
        )
        return self.plugin.data.points.default_daily
