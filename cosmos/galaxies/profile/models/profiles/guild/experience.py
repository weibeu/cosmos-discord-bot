import asyncio
import random

from abc import ABC

from .level import UserLevel


class UserExperience(UserLevel, ABC):

    def __init__(self, **kwargs):
        raw_xp = kwargs.get("stats", dict()).get("xp", dict())
        raw_level = kwargs.get("stats", dict()).get("level", dict())
        self._xp = raw_xp.get("chat", 0)
        super().__init__(raw_level.get("chat", 0))
        self.in_xp_buffer = False

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, xp: int):
        self._xp = int(xp)

    async def give_xp(self):
        xp = random.randint(self.plugin.data.xp.default_min, self.plugin.data.xp.default_max)
        self._xp += xp

        self.in_xp_buffer = True    # Put user in xp cooldown buffer.
        await asyncio.sleep(self.plugin.data.xp.buffer_cooldown)
        self.in_xp_buffer = False
