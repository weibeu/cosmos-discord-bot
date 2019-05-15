import math

from .base import GuildMemberProfileBase
from abc import ABC, abstractmethod


class UserLevel(GuildMemberProfileBase, ABC):

    K = 5777

    def __init__(self, _level: int):
        self._level = _level
        self._xp_level = 0

    @property
    @abstractmethod
    def xp(self):
        raise NotImplementedError

    @property
    def xp_level(self):
        return self._xp_level + math.log(self._level + math.e)*self.K

    @property
    def delta_xp(self):
        return int(self.xp_level - self.xp)

    def from_delta_xp(self):
        while self.xp >= self.xp_level:    # TODO: Remove loop.
            self._xp_level += self.xp_level
            self._level += 1    # Don't really need self._level -= 1 'cause user will never loose xp.
        return self._level

    @property
    def level(self):
        return self.from_delta_xp()

    async def level_up_callback(self):
        pass
