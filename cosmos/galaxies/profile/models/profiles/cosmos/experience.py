import asyncio
import random

from abc import ABC

from .level import UserLevel


class UserExperience(UserLevel, ABC):

    def __init__(self, **kwargs):
        self._xp = kwargs.get("xp", 0)
        super().__init__(kwargs.get("level", 0))
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
