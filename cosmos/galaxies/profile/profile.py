import discord

from .. import Cog
from .models import ProfileCache

from discord.ext import commands


class Profile(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.plugin.profile_cache = ProfileCache(self.plugin)
        self.cache = self.plugin.profile_cache
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
    async def profile(self, ctx, user: discord.User = None):
        user = user or ctx.author
        profile = await self.cache.get_profile(user.id)
        await ctx.send(embed=profile.get_embed())

    @commands.command(name="rep")
    async def rep_user(self, ctx, user: discord.User = None):
        if user and user.bot:
            embed = self.bot.theme.embeds.one_line.primary("😔    Sorry but I just can't do that.")
            return await ctx.send(embed=embed)
        author_profile = await self.cache.get_profile(ctx.author.id)
        if user is None:
            if author_profile.can_rep:
                res = "👌    You can rep someone now."
            else:
                hrs, mins, secs = author_profile.rep_delta
                res = f"🕐    You can rep again in {hrs} hours, {mins} minutes and {secs} seconds."
            embed = self.bot.theme.embeds.one_line.primary(res)
            return await ctx.send(embed=embed)

        if author_profile.can_rep:
            target_profile = await self.cache.get_profile(user.id)
            if not target_profile:
                res = f"😔    Sorry but, {user.name} hasn't created their Cosmos Profile yet. Can you encourage them to?"
                embed = self.bot.theme.embeds.one_line.primary(res)
                await ctx.send(embed=embed)
            await target_profile.rep(author_profile)
            embed = self.bot.theme.embeds.one_line.primary(f"You added one reputation point to {user.name}.", user.avatar_url)
            await ctx.send(embed=embed)
        else:
            hrs, mins, secs = author_profile.rep_delta
            res = f"🕐    You can rep again in {hrs} hours, {mins} minutes and {secs} seconds."
            embed = self.bot.theme.embeds.one_line.primary(res)
            await ctx.send(embed=embed)
