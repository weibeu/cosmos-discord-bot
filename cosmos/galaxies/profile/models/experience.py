import asyncio
import random

from abc import ABC, abstractmethod
from .level import UserLevel


class UserExperience(UserLevel, ABC):

    def __init__(self, xp: int, level):
        super().__init__(level)
        self._xp = xp
        self.in_xp_buffer = False

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, xp: int):
        self._xp = int(xp)

    async def give_xp(self):
        xp = random.randint(self._plugin.data.xp.default_min, self._plugin.data.xp.default_max)
        self._xp += xp

        self.in_xp_buffer = True    # Put user in xp cooldown buffer.
        await asyncio.sleep(self._plugin.data.xp.buffer_cooldown)
        self.in_xp_buffer = False
