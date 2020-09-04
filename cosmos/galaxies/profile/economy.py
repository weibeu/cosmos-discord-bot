"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord

from .. import Cog


class Economy(Cog):
    """Plugin for Cosmos Economy."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    @Cog.listener()
    async def on_dbl_vote(self, profile):
        profile.give_bosons(self.plugin.data.boson.dbl_vote_reward)

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
        try:
            bosons, bonus = await author_profile.take_daily_bosons(target_profile)
        except OverflowError:
            return await ctx.send_line(f"❌    {target_name} can't have such insane number of bosons.")
        new_streak = author_profile.boson_daily_streak
        res = f"{'⭐' if bonus else '🗓'}    {bosons} daily Bosons were given to {target_name}."

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
