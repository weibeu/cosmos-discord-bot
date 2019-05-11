import discord

from .. import Cog


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

    @Cog.listener()
    async def on_message(self, message):
        if self.__is_ignored(message):
            return

        await self.cache.give_assets(message)

    @Cog.group(invoke_without_command=True)
    async def profile(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author
        profile = await self.cache.get_profile(user.id)
        if profile is None:
            res = self.plugin.data.responses.no_profile.format(user_name=user.name)
            return await ctx.send_line(res)
        await ctx.send(embed=await profile.get_embed(ctx.guild.id))

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
            return await ctx.send_line(res)
        profile = await self.cache.get_profile(ctx.author.id)
        await profile.set_description(description)
        embed = self.bot.theme.embeds.primary(title="✅    Your Profile Description has been updated to:")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.description = profile.description
        await ctx.send("", embed=embed)

    @profile.group(name="birthday", aliases=["birthdate", "bday"], invoke_without_command=True)
    async def profile_birthday(self, ctx):
        profile = await self.cache.get_profile(ctx.author.id)
        if not profile.birthday:
            res = "You have not set your birthday on your profile yet."
            return await ctx.send_line(res, ctx.author.avatar_url)
        res = f"Your birthday is on {profile.birthday.strftime('%e %B')}."
        await ctx.send_line(res, ctx.author.avatar_url)

    @profile_birthday.command(name="set")
    async def set_profile_birthday(self, ctx, *, birthday: str):
        profile = await self.cache.get_profile(ctx.author.id)
        await profile.set_birthday(birthday)
        res = f"Your birthday is set to {profile.birthday.strftime('%A, %B %e, %Y')}."
        await ctx.send_line(res, ctx.author.avatar_url)

    @Cog.command(name="rep")
    async def rep_user(self, ctx, *, user: discord.Member = None):
        if user and user.bot:
            return await ctx.send_line("😔    Sorry but I just can't do that.")
        if user and user.id == ctx.author.id:
            return await ctx.send_line("🙂    Nice try but wouldn't that be unfair?")
        author_profile = await self.cache.get_profile(ctx.author.id)
        if user is None:
            if author_profile.can_rep:
                res = "👌    You can rep someone now."
            else:
                res = f"⏳    You can rep again {author_profile.next_rep.humanize()}."
            return await ctx.send_line(res)

        if author_profile.can_rep:
            target_profile = await self.cache.get_profile(user.id)
            if not target_profile:
                res = self.plugin.data.responses.no_profile.format(user_name=user.name)
                return await ctx.send_line(res)
            await target_profile.rep(author_profile)
            res = f"You added one reputation point to {user.name}."
            await ctx.send_line(res, ctx.author.avatar_url)
        else:
            res = f"⏳    You can rep again {author_profile.next_rep.humanize()}."
            await ctx.send_line(res)
