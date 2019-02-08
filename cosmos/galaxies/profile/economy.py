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
            adverb = f"{user.name}, you have"
        if user.bot:
            res = f"😙    Poor {user.name} is jobless. Help them to get one."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        profile = await self.cache.get_profile(user.id)
        if not profile:
            res = self.plugin.data.responses.no_profile.format(user_name=user.name)
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        res = f"💵    {adverb} {profile.bosons} Bosons."
        await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))

    @commands.command(name="daily", aliases=["dailies"])
    async def daily_bosons(self, ctx, user: discord.User = None):
        author_profile = await self.cache.get_profile(ctx.author.id)
        target_name = "you"
        if (user and user.bot) or not user:
            target_profile = author_profile
        else:
            target_profile = await self.cache.get_profile(user.id)
            if target_profile is None:
                target_profile = author_profile
            else:
                target_name = user.name
        if not author_profile.can_take_daily_bosons:
            hrs, mins, secs = author_profile.daily_bosons_delta
            res = f"⏳    You can take your dailies again in {hrs} hours, {mins} minutes and {secs} seconds."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        await author_profile.take_daily_bosons(target_profile)
        res = f"🗓    {self.plugin.data.boson.default_daily} daily Bosons were given to {target_name}."
        await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
