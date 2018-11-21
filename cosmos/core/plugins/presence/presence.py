import discord
import random

import asyncio


class Presence(object):

    def __init__(self, plugin):
        self.plugin = plugin
        self.bot = self.plugin.bot
        self.rotate = self.plugin.data.configs.rotate
        self.bot.loop.create_task(self.rotate_presence())

    async def set_presence(self, activity_type, message, **kwargs):
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
