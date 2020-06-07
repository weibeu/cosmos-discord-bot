from discord.ext import commands

import discord

from .. import Cog


class StatsConverter(commands.Converter):

    STATS = [
        "text", "chat", "voice",
    ]

    async def convert(self, ctx, argument):
        argument = argument.lower()
        if argument not in self.STATS:
            raise commands.BadArgument
        return argument


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

    @staticmethod
    async def __filter(fetch_method, async_fetch_method, documents):
        __documents = []
        for d in documents:
            user_id = d["_id"]
            user = fetch_method(user_id)
            if not user:
                try:
                    user = await async_fetch_method(user_id)
                except discord.NotFound:
                    user = NotFoundUser(user_id)
            d["user"] = user
            __documents.append(d)
        return __documents

    @staticmethod
    async def __entry_parser(ctx, document, documents, show_discriminator=False):
        xp = f"**{document['attribute']}**"
        rank = documents.index(document) + 1
        user = document["user"]
        username = str(user) if show_discriminator else user.name
        if rank == 1:
            entry = f"🥇    {username}", xp
        elif rank == 2:
            entry = f"🥈    {username}", xp
        elif rank == 3:
            entry = f"🥉    {username}", xp
        else:
            entry = f"#**{rank}**    {username}", xp

        if user.id == ctx.author.id:
            entry = f"{ctx.emotes.misc.favorite}    **{username}**", entry[1]

        return entry

    async def __xp_entry_parser(self, ctx, document, documents):
        key, value = await self.__entry_parser(ctx, document, documents, show_discriminator=True)
        return key, f"`TOTAL XP:` {value}"

    async def __global_xp_entry_parser(self, *args, **kwargs):
        key, value = await self.__entry_parser(*args, **kwargs)
        return key, f"`TOTAL GLOBAL XP:` {value}"

    async def __show_leaderboards(self, ctx, entries, name, parser, global_=False):
        paginator = ctx.get_field_paginator(entries, entry_parser=parser, inline=False, per_page=9)
        icon = self.bot.theme.images.physics if global_ else ctx.guild.icon_url
        paginator.embed.set_author(name=name, icon_url=icon)
        await paginator.paginate()

    @Cog.group(name="leaderboards", aliases=["leaderboard", "lb"], invoke_without_command=True, inescapable=False)
    async def leaderboards(self, ctx, stats: StatsConverter = "chat"):
        """Displays top members with maximum chat experience points."""
        profile = await ctx.fetch_member_profile()

        if stats in ("chat", "text"):
            filter_ = f"{profile.guild_filter}.stats.xp.chat"
            name = f"{ctx.guild.name} Chat XP Leaderboards".upper()
        else:
            raise ValueError
        entries = await self.__filter(ctx.guild.get_member, ctx.guild.fetch_member, await self.fetch_top(filter_))
        await self.__show_leaderboards(ctx, entries, name, self.__xp_entry_parser)

    @leaderboards.command(name="global", aliases=["cosmos", "globals"])
    async def global_leaderboards(self, ctx, stats: StatsConverter = "chat"):
        """Displays top users with maximum chat experience earned globally across all servers."""

        if stats in ("chat", "text"):
            filter_ = "stats.xp.chat"
            name = f"Cosmos Universe Chat XP Leaderboards".upper()
        else:
            raise ValueError
        entries = await self.__filter(self.bot.get_user, self.bot.fetch_user, await self.fetch_top(filter_))
        await self.__show_leaderboards(ctx, entries, name, self.__global_xp_entry_parser, True)
