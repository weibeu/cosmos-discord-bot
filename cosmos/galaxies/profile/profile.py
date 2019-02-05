from discord.ext import commands

from .. import Cog
from .models import ProfileCache


class Profile(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = ProfileCache(self.plugin)
        if self.plugin.data.profile.__dict__.get("cache_all"):
            self.bot.loop.create_task(self.cache.prepare())

    def __is_ignored(self, message):
        if message.author.id == self.bot.user.id:
            return True
        if message.author.bot:
            return True
        if not message.guild:
            return True

    async def on_message(self, message):
        if self.__is_ignored(message):
            return

        await self.cache.give_xp(message)

    @commands.command()
    async def profile(self, ctx):
        embed = await self.cache.get_profile_embed(ctx)
        await ctx.send(embed=embed)
