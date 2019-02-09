import discord

from .. import Cog

from discord.ext import commands


class Profile(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache
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

        await self.cache.give_assets(message)

    @commands.group(invoke_without_command=True)
    async def profile(self, ctx, user: discord.User = None):
        user = user or ctx.author
        profile = await self.cache.get_profile(user.id)
        if profile is None:
            res = self.plugin.data.responses.no_profile.format(user_name=user.name)
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        await ctx.send(embed=profile.get_embed())

    @profile.group(name="description", aliases=["text"], invoke_without_command=True)
    async def profile_description(self, ctx):
        profile = await self.cache.get_profile(ctx.author.id)
        embed = self.bot.theme.embeds.primary(title="Profile Description:")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.description = profile.description
        await ctx.send(embed=embed)

    @profile_description.command(name="set", aliases=["modify", "edit", "change"])
    async def set_profile_description(self, ctx, *, description: str):
        max_words = self.plugin.data.profile.max_description_length
        if len(description) > max_words:
            res = f"❌    Sorry but profile description cannot exceed {max_words} word limit."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        profile = await self.cache.get_profile(ctx.author.id)
        await profile.set_description(description)
        embed = self.bot.theme.embeds.primary(title="✅    Your Profile Description has been updated to:")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.description = profile.description
        await ctx.send("", embed=embed)

    @commands.command(name="rep")
    async def rep_user(self, ctx, user: discord.User = None):
        if user and user.bot:
            embed = self.bot.theme.embeds.one_line.primary("😔    Sorry but I just can't do that.")
            return await ctx.send(embed=embed)
        if user and user.id == ctx.author.id:
            res = "🙂    Nice try but wouldn't that be unfair?"
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
        author_profile = await self.cache.get_profile(ctx.author.id)
        if user is None:
            if author_profile.can_rep:
                res = "👌    You can rep someone now."
            else:
                hrs, mins, secs = author_profile.rep_delta
                res = f"⏳    You can rep again in {hrs} hours, {mins} minutes and {secs} seconds."
            return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))

        if author_profile.can_rep:
            target_profile = await self.cache.get_profile(user.id)
            if not target_profile:
                res = self.plugin.data.responses.no_profile.format(user_name=user.name)
                return await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
            await target_profile.rep(author_profile)
            res = f"You added one reputation point to {user.name}."
            await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res, ctx.author.avatar_url))
        else:
            hrs, mins, secs = author_profile.rep_delta
            res = f"⏳    You can rep again in {hrs} hours, {mins} minutes and {secs} seconds."
            await ctx.send(embed=self.bot.theme.embeds.one_line.primary(res))
