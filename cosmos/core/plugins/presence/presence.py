import discord


class Presence(object):

    def __init__(self, bot):
        self.bot = bot

    async def set_presence(self, activity):
        try:
            await self.bot.change_presence(activity=activity)
        except discord.errors.InvalidArgument:
            return
