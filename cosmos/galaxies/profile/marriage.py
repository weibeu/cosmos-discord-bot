import asyncio

import discord
from discord.ext import commands

from .. import Cog


class Marriage(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    @commands.group(name="propose", aliases=["proposal", "proposals"], invoke_without_command=True)
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
        if author_profile.proposed:
            res = f"You've already proposed to {author_profile.proposed.name}. You need to cancel your proposal first."
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
            content = f"{ctx.author.mention} {user.mention}"
            res = f"💕    The perfect match! You both have proposed to each other. You should now kiss each other " \
                f"under 60 seconds to finally get married till eternity."
            await ctx.send(content, embed=self.bot.theme.embeds.one_line.primary(res))
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

    @propose_user.command(name="decline", aliases=["reject"])
    async def decline_proposal(self, ctx):
        author_profile = await self.cache.get_profile(ctx.author.id)
        if not author_profile.proposer:
            res = f"{ctx.author.name}, you do not have any pending proposals."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res, ctx.author.avatar_url))
        target_profile = await self.cache.get_profile(author_profile.proposer_id)
        await author_profile.decline_proposal(target_profile)
        try:
            res = f"💔    {ctx.author.name} has declined your proposal."
            await target_profile.user.send(embed=self.bot.theme.embeds.one_line.primary(res))
        except discord.Forbidden:
            pass
        res = f"You have declined the proposal of {target_profile.user.name}."
        await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res, ctx.author.avatar_url))

    @propose_user.command(name="cancel", aliases=["revoke", "pull"])
    async def cancel_proposal(self, ctx):
        author_profile = await self.cache.get_profile(ctx.author.id)
        if not author_profile.proposed:
            res = f"{ctx.author.name}, you have not sent any proposals yet."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res, ctx.author.avatar_url))
        target_profile = await self.cache.get_profile(author_profile.proposed_id)
        await author_profile.cancel_proposal(target_profile)
        try:
            res = f"💔    {ctx.author.name} has pulled back their proposal from you."
            await target_profile.user.send(embed=self.bot.theme.embeds.one_line.primary(res))
        except discord.Forbidden:
            pass
        res = f"You have cancelled your proposal sent to {target_profile.user.name}."
        await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res, ctx.author.avatar_url))

    @commands.command(name="divorce")
    async def divorce_user(self, ctx):
        author_profile = await self.cache.get_profile(ctx.author.id)
        if not author_profile.spouse:
            res = "You are not married yet to divorce."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res, ctx.author.avatar_url))
        target_profile = await self.cache.get_profile(author_profile.spouse.id)
        await author_profile.divorce(target_profile)
        try:
            res = f"💔    {ctx.author.name} has divorced you."
            await target_profile.user.send(embed=self.bot.theme.embeds.one_line.primary(res))
        except discord.Forbidden:
            pass
        res = f"You have divorced {target_profile.user.name}."
        await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res, ctx.author.avatar_url))
