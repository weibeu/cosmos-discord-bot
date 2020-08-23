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

from .models.profiles import CosmosUserProfile
from discord.ext import commands

import arrow
import discord

from .. import Cog


class StatsConverter(commands.Converter):

    STATS = list()

    @classmethod
    async def convert(cls, ctx, argument):
        argument = argument.lower()
        if argument not in cls.STATS:
            argument = f"{argument}s"
            if argument not in cls.STATS:
                raise commands.BadArgument
        return argument


class GuildStatsConverter(StatsConverter):

    STATS = [
        "text", "chat", "voice", "points", "streaks",
    ]

    async def convert(self, ctx, argument):
        try:
            return await super().convert(ctx, argument)
        except commands.BadArgument:
            return await GlobalStatsConverter.convert(ctx, argument)


class GlobalStatsConverter(StatsConverter):

    STATS = [
        "text", "chat", "voice", "bosons", "fermions", "reputations", "reps", "streaks", "marriages", "relationships",
    ]


class NotFoundUser(discord.Object):

    def __str__(self):
        return str(self.id)

    @property
    def name(self):
        return self.__str__()


class Leaderboards(Cog):
    """Leaderboard commands over various properties of user profile."""

    INESCAPABLE = False

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def fetch_top(self, filter_, limit=111):
        pipeline = [
            {"$project": {"_id": False, "user_id": True, filter_: True}},
            {"$match": {filter_: {"$exists": True}}},
            {"$group": {
                "_id": "$user_id", "attribute": {"$max": f"${filter_}"}
            }},
            {"$sort": {"attribute": -1}}, {"$limit": limit}
        ]
        return await self.plugin.cache.collection.aggregate(pipeline).to_list(None)

    async def __filter(self, fetch_method, async_fetch_method, documents):
        __documents = []
        for d in documents:
            user_id = d["_id"]
            user = fetch_method(user_id)
            if not user:
                try:
                    user = await async_fetch_method(user_id)
                    if isinstance(user, discord.User):
                        # noinspection PyProtectedMember
                        self.bot._connection._users[user.id] = user
                    elif isinstance(user, discord.Member):
                        # noinspection PyProtectedMember
                        user.guild._add_member(user)
                except discord.NotFound:
                    user = NotFoundUser(user_id)
            d["user"] = user
            __documents.append(d)
        return __documents

    @staticmethod
    async def __entry_parser(ctx, document, documents, show_discriminator=False):
        rank = documents.index(document) + 1
        user = document["user"]
        username = str(user) if show_discriminator else user.name
        if rank == 1:
            entry = f"🥇    {username}"
        elif rank == 2:
            entry = f"🥈    {username}"
        elif rank == 3:
            entry = f"🥉    {username}"
        else:
            entry = f"#**{rank}**    {username}"

        if user.id == ctx.author.id:
            entry = f"{ctx.emotes.misc.favorite}    **{username}**"

        return entry, document['attribute']

    async def __xp_entry_parser(self, ctx, document, documents):
        key, xp = await self.__entry_parser(ctx, document, documents, show_discriminator=True)
        xp = xp / CosmosUserProfile.CHAT_XP_CONSTRAIN
        return key, f"`TOTAL XP:` **{round(xp)}**"

    async def __voice_xp_entry_parser(self, *args, **kwargs):
        key, xp = await self.__entry_parser(*args, **kwargs)
        xp = xp / CosmosUserProfile.VOICE_XP_CONSTRAIN
        return key, f"`TOTAL XP:` **{round(xp)}**"

    async def __points_parser(self, *args, **kwargs):
        key, value = await self.__entry_parser(*args, show_discriminator=True, **kwargs)
        return key, f"`POINTS:` **{value}**"

    async def __show_leaderboards(self, ctx, entries, name, parser, global_=False):
        paginator = ctx.get_field_paginator(entries, entry_parser=parser, inline=False, per_page=9)
        icon = self.bot.theme.images.physics if global_ else ctx.guild.icon_url
        paginator.embed.set_author(name=name, icon_url=icon)
        await paginator.paginate()

    @Cog.group(name="leaderboards", aliases=["leaderboard", "lb"], invoke_without_command=True, inescapable=False)
    async def leaderboards(self, ctx, stats: GuildStatsConverter = "chat"):
        """Displays top members with maximum chat experience points."""
        profile = await ctx.fetch_member_profile()

        if stats in ("chat", "text"):
            filter_ = f"stats.xp.chat"
            name = "Chat XP Leaderboards"
            parser = self.__xp_entry_parser
        elif stats == "voice":
            filter_ = "stats.xp.voice"
            name = "Voice XP Leaderboards"
            parser = self.__voice_xp_entry_parser
        elif stats == "points":
            filter_ = "points.points"
            name = "Points Leaderboards"
            parser = self.__points_parser
        elif stats == "streaks":
            filter_ = "points.daily_streak"
            name = "Points Daily Streak Leaderboards"
            parser = self.__streaks_parser
        else:
            # noinspection PyTypeChecker
            return await self.global_leaderboards(ctx, stats)
        filter_ = f"{profile.guild_filter}.{filter_}"
        name = f"{ctx.guild.name} {name}".upper()
        async with ctx.loading():
            entries = await self.__filter(ctx.guild.get_member, ctx.guild.fetch_member, await self.fetch_top(filter_))
        await self.__show_leaderboards(ctx, entries, name, parser)

    async def __global_xp_entry_parser(self, *args, **kwargs):
        key, value = await self.__entry_parser(*args, **kwargs)
        return key, f"`TOTAL GLOBAL XP:` **{value}**"

    async def __global_voice_xp_entry_parser(self, *args, **kwargs):
        return await self.__global_xp_entry_parser(*args, **kwargs)

    async def __bosons_parser(self, *args, **kwargs):
        key, value = await self.__entry_parser(*args, **kwargs)
        return key, f"`BOSONS:` **{value}**"

    async def __reps_parser(self, *args, **kwargs):
        key, value = await self.__entry_parser(*args, **kwargs)
        return key, f"`REPUTATION POINTS:` **{value}**"

    async def __fermions_parser(self, *args, **kwargs):
        key, value = await self.__entry_parser(*args, **kwargs)
        return key, f"`FERMIONS:` **{value}**"

    async def __streaks_parser(self, *args, **kwargs):
        key, value = await self.__entry_parser(*args, **kwargs)
        return key, f"`DAILY STREAKS:` **{value}**"

    async def __marriages_parser(self, *args, **kwargs):
        key, value = await self.__entry_parser(*args, **kwargs)
        return key, f"`MARRIED:` **{arrow.get(value).humanize()}.**"

    @leaderboards.command(name="global", aliases=["cosmos", "globals"])
    async def global_leaderboards(self, ctx, stats: GlobalStatsConverter = "chat"):
        """Displays top users with maximum chat experience earned globally across all servers."""

        if stats in ("chat", "text"):
            filter_ = "stats.xp.chat"
            name = "Chat XP Leaderboards"
            parser = self.__global_xp_entry_parser
        elif stats == "voice":
            filter_ = "stats.xp.voice"
            name = "Voice XP Leaderboards"
            parser = self.__global_voice_xp_entry_parser
        elif stats == "bosons":
            filter_ = "currency.bosons"
            name = "Bosons Leaderboards"
            parser = self.__bosons_parser
        elif stats in ("reps", "reputations"):
            filter_ = "reputation.points"
            name = "Reputation Leaderboards"
            parser = self.__reps_parser
        elif stats == "fermions":
            filter_ = "currency.fermions"
            name = "Fermions Leaderboards"
            parser = self.__fermions_parser
        elif stats == "streaks":
            filter_ = "currency.bosons_daily_streak"
            name = "Bosons Daily Streak Leaderboards"
            parser = self.__streaks_parser
        elif stats in ("marriages", "relationships"):
            filter_ = "relationship.marriage.timestamp"
            name = "Eternal Relationship Leaderboards"
            parser = self.__marriages_parser
        else:
            raise ValueError
        async with ctx.loading():
            entries = await self.__filter(self.bot.get_user, self.bot.fetch_user, await self.fetch_top(filter_))
        name = f"Cosmos Universe {name}".upper()
        await self.__show_leaderboards(ctx, entries, name, parser, True)
