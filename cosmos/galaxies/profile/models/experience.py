import asyncio
import random

from abc import ABC, abstractmethod
from cosmos.galaxies.profile.models.base import ProfileModelsBase


class UserExperience(ProfileModelsBase, ABC):

    @property
    @abstractmethod
    def _plugin(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def xp_buffer_cooldown(self):
        raise NotImplementedError

    def __init__(self, xp: int):
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
        self.in_xp_buffer = True
        await asyncio.sleep(self.xp_buffer_cooldown)
        self.in_xp_buffer = False
