import asyncio

import discord
from discord.ext import commands

from .. import Cog


class Marriage(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    @commands.command(name="propose")
    async def propose_user(self, ctx, user: discord.User):
        if user.bot or user.id == ctx.author.id:
            res = f"😶    You are really weird. But I understand your feelings {ctx.author.name}."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        target_profile = await self.cache.get_profile(user.id)
        if target_profile.spouse:
            res = f"💔    ... sorry to inform you but uh {user.name} is already married."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        author_profile = await self.cache.get_profile(ctx.author.id)
        if author_profile.spouse:
            res = f"😒    By any chance do you still remember {author_profile.spouse.name}?"
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))

        def check_kiss_author(msg):
            if msg.author.id == ctx.author.id and "kiss" in msg.content.lower() and msg.mentions:
                if msg.mentions[0].id == user.id:
                    return True
            return False

        def check_kiss_target(msg):
            if msg.author.id == user.id and "kiss" in msg.content.lower() and msg.mentions:
                if msg.mentions[0].id == ctx.author.id:
                    return True
            return False

        if target_profile.proposed and target_profile.proposed.id == ctx.author.id:
            res = f"💕    The perfect match! You both have proposed to each other. You should now kiss each other " \
                f"under 60 seconds to finally get married till eternity."
            await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
            try:
                _ = await self.bot.wait_for("message", check=check_kiss_author)
                __ = await self.bot.wait_for("message", check=check_kiss_target)
            except asyncio.TimeoutError:
                res = "🕛    Time is up. Thought you can always give it another shot."
                return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
            await target_profile.marry(author_profile)
            content = f"{ctx.author.mention} {user.mention}"
            res = f"🎉    Congratulations {ctx.author.name} and {user.name}! You're married now."
            return await ctx.send(content, embed=self.bot.theme.embeds.one_line.primary(res))

        if target_profile.proposer:
            res = f"😔    Someone has already proposed to {user.name}. They should decline them first right?"
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))

        await target_profile.propose(author_profile)
        try:
            res = f"💖    {ctx.author} has proposed you."
            await user.send(embed=self.bot.theme.embeds.one_line.primary(res))
        except discord.Forbidden:
            pass
        res = f"💖    You have proposed to {user.name}!"
        await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
