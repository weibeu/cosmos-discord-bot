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

import time
import asyncio
import random

from abc import ABC

from .level import UserLevel, MemberLevel


class UserExperience(UserLevel, ABC):

    CHAT_XP_CONSTRAIN = 1
    VOICE_XP_CONSTRAIN = 23

    def __init__(self, **kwargs):
        raw_xp = kwargs.get("stats", dict()).get("xp", dict())
        self._xp = raw_xp.get("chat", 0)
        self._voice_xp = raw_xp.get("voice", 0)
        self.in_xp_buffer = False
        self.is_speaking = False
        self.__voice_activity_time = None
        self.__voice_level = self.level

    def get_total_xp(self, level):
        return sum(self.LEVELS_XP[: level])

    @property
    def xp(self):
        return round(self._xp / self.CHAT_XP_CONSTRAIN)

    @xp.setter
    def xp(self, xp: int):
        self._xp = int(xp)

    async def give_xp(self, channel):
        last_level = self.level

        xp = random.randint(self.plugin.data.xp.default_min, self.plugin.data.xp.default_max)
        self._xp += xp

        if self.level > last_level:
            self.plugin.bot.loop.create_task(self.level_up_callback(channel))

        self.in_xp_buffer = True    # Put user in xp cooldown buffer.
        await asyncio.sleep(self.plugin.data.xp.buffer_cooldown)
        self.in_xp_buffer = False

    def cache_voice_xp(self):
        self._voice_xp += round(time.time() - (self.__voice_activity_time or time.time()))
        self.__voice_activity_time = time.time() if self.is_speaking else None
        if self.voice_level > self.__voice_level:
            self.__voice_level = self.voice_level    # Update the counter.
            self.plugin.bot.loop.create_task(self.voice_level_up_callback())

    @property
    def voice_xp(self):
        if self.is_speaking:
            raw_xp = self._voice_xp + round(time.time() - (self.__voice_activity_time or time.time()))
        else:
            raw_xp = self._voice_xp
        return round(raw_xp / self.VOICE_XP_CONSTRAIN)

    def record_voice_activity(self):
        if not self.is_speaking:
            self.__voice_activity_time = time.time()
            self.is_speaking = True
            self.__voice_level = self.voice_level    # Save current voice level.
            # print(f'opened {self.name}')
        else:
            pass

    def close_voice_activity(self):
        if self.is_speaking:
            self.is_speaking = False
            self.cache_voice_xp()
            # print(f'closed {self.name}')
        else:
            pass

    @property
    def delta_xp(self):
        return self.get_total_xp(self.level + 1) - self.xp

    @property
    def delta_voice_xp(self):
        return self.get_total_xp(self.voice_level + 1) - self.voice_xp

    @property
    def xp_progress(self):
        return self.xp - self.get_total_xp(self.level), self.LEVELS_XP[self.level]

    @property
    def voice_xp_progress(self):
        return self.voice_xp - self.get_total_xp(self.voice_level), self.LEVELS_XP[self.voice_level]


class MemberExperience(MemberLevel, UserExperience, ABC):

    pass
