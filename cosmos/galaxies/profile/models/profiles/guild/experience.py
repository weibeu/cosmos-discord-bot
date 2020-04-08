import time
import asyncio
import random

from abc import ABC

from .level import UserLevel, MemberLevel


class UserExperience(UserLevel, ABC):

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
        return self._xp

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
        return round(raw_xp / 17)

    def record_voice_activity(self):
        self.__voice_activity_time = time.time()
        self.is_speaking = True
        self.__voice_level = self.voice_level    # Save current voice level.

    def close_voice_activity(self):
        self.is_speaking = False
        self.cache_voice_xp()

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
