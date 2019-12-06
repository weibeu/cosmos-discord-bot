import time
import asyncio
import random

from abc import ABC

from .level import UserLevel


class UserExperience(UserLevel, ABC):

    def __init__(self, **kwargs):
        raw_xp = kwargs.get("stats", dict()).get("xp", dict())
        self._xp = raw_xp.get("chat", 0)
        self._voice_xp = raw_xp.get("voice", 0)
        self.in_xp_buffer = False
        self.is_speaking = False
        self.__voice_activity_time = None

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, xp: int):
        self._xp = int(xp)

    async def give_xp(self):
        last_level = self.level

        xp = random.randint(self.plugin.data.xp.default_min, self.plugin.data.xp.default_max)
        self._xp += xp

        if self.level > last_level:
            self.plugin.bot.loop.create_task(self.level_up_callback())

        self.in_xp_buffer = True    # Put user in xp cooldown buffer.
        await asyncio.sleep(self.plugin.data.xp.buffer_cooldown)
        self.in_xp_buffer = False

    @property
    def voice_xp(self):
        if self.is_speaking:
            return self._voice_xp + round(time.time() - self.__voice_activity_time)
        return self._voice_xp

    def record_voice_activity(self):
        self.is_speaking = True
        self.__voice_activity_time = time.time()
        # TODO: Also record voice activity of members who are already in voice channel on_ready.

    def close_voice_activity(self):
        _level = self.voice_level

        self._voice_xp += round(time.time() - self.__voice_activity_time)

        if self.voice_level > _level:
            self.plugin.bot.loop.create_task(self.level_up_callback())

        self.is_speaking = False
        self.__voice_activity_time = None
