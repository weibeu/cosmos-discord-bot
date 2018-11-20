import discord


class Presence(object):

    def __init__(self, plugin):
        self.plugin = plugin
        self.bot = self.plugin.bot

    async def set_presence(self, activity_type, **kwargs):
        if isinstance(activity_type, str):
            try:
                activity_type = getattr(discord.ActivityType, activity_type)
            except AttributeError:
                self.bot.log.error("Unknown discord.ActivityType specified.")
                self.bot.eh.sentry.capture_exception()
        try:
            if activity_type == discord.ActivityType.playing:
                await self.bot.change_presence(activity=discord.Game(**kwargs))
            elif activity_type == discord.ActivityType.streaming:
                await self.bot.change_presence(activity=discord.Streaming(**kwargs))
            else:
                await self.bot.change_presence(activity=discord.Activity(type=activity_type, **kwargs))
        except discord.errors.InvalidArgument:
            self.bot.eh.sentry.capture_exception()

    """async def rotate_presence(self):
        # rotate presence on certain time interval."""
