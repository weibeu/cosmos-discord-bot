import asyncio
import random

import discord

from ..admin.base import Admin


class Presence(Admin):

    def __init__(self, plugin):
        super().__init__(plugin)
        self.rotate = self.plugin.data.configs.rotate
        self.rotate_task = self.bot.loop.create_task(self.rotate_presence())
        # Inject version and release.
        release_meta = f"{self.bot.release} - {self.bot.version}"
        self.plugin.data.messages.playing.append(release_meta)
        self.plugin.data.messages.streaming.append(release_meta)

    def cog_unload(self):
        self.bot.log.info("Stopping presence rotation.")
        self.rotate_task.cancel()
        self.bot.loop.create_task(self.set_presence())

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

    async def rotate_presence(self):
        await self.bot.wait_until_ready()
        while self.rotate:
            args = self._get_args()
            await self.set_presence(*args)
            await asyncio.sleep(self.plugin.data.configs.interval)
