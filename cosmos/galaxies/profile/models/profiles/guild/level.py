"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from .base import GuildMemberProfileBase
from abc import ABC, abstractmethod


class UserLevel(ABC):

    @property
    @abstractmethod
    def plugin(self):
        raise NotImplementedError

    # K = 5777
    LEVELS_XP = [5 * (i ** 2) + 50 * i + 100 for i in range(200)]

    def get_level(self, xp):
        level = 0
        while xp >= self.LEVELS_XP[level]:
            xp -= self.LEVELS_XP[level]
            level += 1
        return level

    @property
    @abstractmethod
    def xp(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def voice_xp(self):
        raise NotImplementedError

    # @property
    # def xp_level(self):
    #     return self._xp_level + math.log(self._level + math.e)*self.K

    # @property
    # def delta_xp(self):
    #     return int(self.xp_level - self.xp)
    #
    # def from_delta_xp(self):
    #     while self.xp >= self.xp_level:
    #         self._xp_level += self.xp_level
    #         self._level += 1    # Don't really need self._level -= 1 'cause user will never loose xp.
    #     return self._level

    @property
    def level(self):
        return self.get_level(self.xp)

    @property
    def voice_level(self):
        return self.get_level(self.voice_xp)

    async def level_up_callback(self, channel):
        pass

    async def voice_level_up_callback(self):
        pass


class MemberLevel(GuildMemberProfileBase, UserLevel, ABC):

    async def level_up_callback(self, _):
        self.plugin.bot.dispatch("text_level_up", self, _)

    async def voice_level_up_callback(self):
        self.plugin.bot.dispatch("voice_level_up", self)
