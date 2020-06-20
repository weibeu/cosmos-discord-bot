import discord

from .. import Cog


class Economy(Cog):
    """Plugin for Cosmos Economy."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    @Cog.group(name="bosons", aliases=["boson", "$"], invoke_without_command=True)
    async def bosons(self, ctx, *, user: discord.Member = None):
        """Displays Bosons earned by you or specified member."""
        if user:
            adverb = f"{user.name} has"
        else:
            user = ctx.author
            adverb = f"{user.name}, you have"
        if user.bot:
            res = f"😙    Poor {user.name} is jobless. Help them to get one."
            return await ctx.send_line(res)
        profile = await self.cache.get_profile(user.id)
        if not profile:
            res = self.plugin.data.responses.no_profile.format(user_name=user.name)
            return await ctx.send_line(res)
        res = f"💵    {adverb} {profile.bosons} Bosons."
        await ctx.send_line(res)

    @bosons.command(name="credit", aliases=["transfer", "give"])
    async def transfer_bosons(self, ctx, bosons: int, *, user: discord.Member):
        """Transfer your Bosons to specified member."""
        if user.bot:
            return await ctx.send_line("❌    They don't really need it.")
        if bosons < 0:
            return await ctx.send_line("❌    Sorry but my calculations involving negative numbers sucks.")
        author_profile = await self.cache.get_profile(ctx.author.id)
        target_profile = await self.cache.get_profile(user.id)
        if target_profile is None:
            res = self.plugin.data.responses.no_profile.format(user_name=user.name)
            return await ctx.send_line(res)
        if author_profile.bosons < bosons:
            res = "❌    Sorry but you don't have enough Bosons to complete this transaction."
            return await ctx.send_line(res)
        author_profile.give_bosons(-bosons)

        try:
            target_profile.give_bosons(bosons)
        except OverflowError:
            return await ctx.send_line("❌    They can't have such insane number of bosons.")

        res = f"📤    {ctx.author.name}, you gave {bosons} Bosons to {user.name}."
        await ctx.send_line(res)

    @Cog.command(name="daily", aliases=["dailies"])
    async def daily_bosons(self, ctx, *, user: discord.Member = None):
        """Lets you claim your daily Bosons. Specify any member to let them have your daily Bosons."""
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
            res = f"⏳    You can take your dailies again {author_profile.next_daily_bosons.humanize()}."
            return await ctx.send_line(res)

        old_streak = author_profile.boson_daily_streak
        bosons = await author_profile.take_daily_bosons(target_profile)
        new_streak = author_profile.boson_daily_streak
        res = f"🗓    {bosons} daily Bosons were given to {target_name}."

        if old_streak > 0:
            if not new_streak:
                res = f"{res} | ☹ x{old_streak} Streak expired."
            else:
                res = f"{res} | 🌟 x{new_streak} Streak!"
        else:
            res = f"{res} | Keep up the streaks!"

        await ctx.send_line(res)

    @Cog.command(name="fermions", aliases=["fermion"])
    async def fermions(self, ctx):
        """Displays number of Fermions you have."""
        profile = await ctx.fetch_cosmos_user_profile()
        await ctx.send_line(f"🔷    {ctx.author.name}, you have {profile.fermions} fermions.")
