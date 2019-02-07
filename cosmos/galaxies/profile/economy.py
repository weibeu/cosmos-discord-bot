import discord

from .. import Cog
from discord.ext import commands


class Economy(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.profile_cache

    @commands.command(name="bosons", aliases=["boson", "$"])
    async def bosons(self, ctx, user: discord.User = None):
        if user:
            adverb = f"{user.name} has"
        else:
            user = ctx.author
            adverb = "{user.name}, you have"
        if user.bot:
            res = f"😙    Poor {user.name} is jobless. Help them to get one."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        profile = await self.cache.get_profile(user.id)
        if not profile:
            res = self.plugin.data.responses.no_profile.format(user_name=user.name)
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        res = f"💵    {adverb} {profile.bosons} Bosons."
        await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
