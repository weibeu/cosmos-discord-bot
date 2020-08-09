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

import asyncio
import random

import discord

from discord.ext import tasks
from ..admin.base import Admin


class Presence(Admin):

    UPDATE_INTERVAL = 17

    def __init__(self, plugin):
        super().__init__(plugin)
        self.rotate = self.plugin.data.configs.rotate
        # Inject version and release.
        release_meta = f"{self.bot.release} - {self.bot.version}"
        self.plugin.data.messages.playing.append(release_meta)
        self.plugin.data.messages.streaming.append(release_meta)
        self.update_presence.start()

    async def set_presence(self, activity_type=None, message=None, **kwargs):
        if activity_type is None and message is None:
            await self.bot.change_presence(activity=None)
            return
        if isinstance(activity_type, str):
            try:
                activity_type = getattr(discord.ActivityType, activity_type)
            except AttributeError:
                self.bot.log.error("Unknown discord.ActivityType specified.")
                self.bot.eh.sentry.capture_exception()
        try:
            if activity_type == discord.ActivityType.playing:
                await self.bot.change_presence(activity=discord.Game(message, **kwargs))
            elif activity_type == discord.ActivityType.streaming:
                stream_url = self.plugin.data.configs.stream_url
                await self.bot.change_presence(activity=discord.Streaming(name=message, url=stream_url, **kwargs))
            else:
                await self.bot.change_presence(activity=discord.Activity(type=activity_type, name=message, **kwargs))
        except discord.errors.InvalidArgument:
            self.bot.eh.sentry.capture_exception()

    def _get_args(self):
        activity = self.plugin.data.configs.activity_type
        if activity.upper() == "RANDOM":
            activity_type = random.choice(list(self.plugin.data.messages.__dict__))
            message = random.choice(getattr(self.plugin.data.messages, activity_type))
            return tuple([activity_type, message])
        else:
            try:
                message = random.choice(getattr(self.plugin.data.messages, activity))
            except AttributeError:
                self.bot.log.error(f"Can't find list of messages for '{activity}'.")
                self.bot.eh.sentry.capture_exception()
            else:
                activity_type = activity
                return tuple([activity_type, message])

    @tasks.loop(seconds=UPDATE_INTERVAL)
    async def update_presence(self):
        args = self._get_args()
        # noinspection PyBroadException
        try:
            await self.set_presence(*args)
        except Exception:
            await asyncio.sleep(self.plugin.data.configs.interval)

    @update_presence.before_loop
    async def before_update_presence(self):
        await self.bot.wait_until_ready()
