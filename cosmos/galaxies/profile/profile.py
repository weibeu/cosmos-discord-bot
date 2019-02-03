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

    @commands.command()
    async def profile(self, ctx):
        embed = await self.cache.get_profile_embed(ctx)
        await ctx.send(embed=embed)
