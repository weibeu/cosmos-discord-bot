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

from cosmos import exceptions
from abc import ABC

import arrow

from .tags import UserTags
from .family import Relationship
from .prime import CosmosUserPrime
from .currency import Boson, Fermion

from ..guild import GuildMemberProfile, UserExperience


class CosmosUserProfile(CosmosUserPrime, Boson, Fermion, UserExperience, Relationship, UserTags, ABC):

    @property
    def plugin(self):
        return self._plugin

    @property
    def collection(self):
        return self.__collection

    @property
    def id(self):
        return self._id

    @property
    def description(self):
        return self._description or self.plugin.data.profile.default_description

    @classmethod
    def from_document(cls, plugin, document: dict):
        return cls(plugin, **document)

    def __init__(self, plugin, **kwargs):
        self._plugin = plugin
        CosmosUserPrime.__init__(self, **kwargs.get("prime", dict()))
        Boson.__init__(self, **kwargs)
        Fermion.__init__(self, **kwargs)
        UserExperience.__init__(self, **kwargs)
        Relationship.__init__(self, **kwargs)
        UserTags.__init__(self, kwargs.get("tags", dict()))
        self._id: int = kwargs["user_id"]
        raw_reputation = kwargs.get("reputation", dict())
        self.reps: int = raw_reputation.get("points", 0)
        self.rep_timestamp = self.get_arrow(raw_reputation.get("timestamp"))
        # self.badges = []
        self._description: str = kwargs.get("description", str())
        self.birthday = self.get_arrow(kwargs.get("birthday"))
        self.rank = None
        # self.inventory = []
        # self.on_time: int = None
        self.guild_profiles = self.plugin.bot.cache.lru(self.plugin.data.profile.guild_profiles_cache_max_size)
        self.__collection = self.plugin.collection
        if self.plugin.data.profile.fetch_guild_profiles:
            self.plugin.bot.create_task(self.__fetch_guild_profiles())    # TODO: Fetch profiles of all guilds.

    @property
    def can_rep(self):
        if not self.rep_timestamp:    # Using rep for first time.
            return True
        return arrow.utcnow() > self.next_rep

    @property
    def next_rep(self):
        return self.get_future_arrow(self.rep_timestamp, hours=self.plugin.data.profile.rep_cooldown)

    async def rep(self, author_profile):
        self.reps += 1
        author_profile.rep_timestamp = arrow.utcnow()
        await self.collection.update_one(
            self.document_filter, {"$set": {"reputation.points": self.reps}}
        )
        await self.collection.update_one(
            author_profile.document_filter, {"$set": {"reputation.timestamp": author_profile.rep_timestamp.datetime}}
        )

    async def set_description(self, description: str):
        self._description = description
        await self.collection.update_one(
            self.document_filter, {"$set": {"description": self.description}}
        )

    async def set_birthday(self, birthday):
        if isinstance(birthday, str):
            try:
                birthday = arrow.get(birthday, "DD-MM-YYYY")
            except arrow.parser.ParserMatchError:
                try:
                    birthday = arrow.get(birthday, "DD/MM/YYYY")
                except arrow.parser.ParserMatchError:
                    birthday = arrow.get(birthday, "D MMMM YYYY")
        self.birthday = birthday

        await self.collection.update_one(
            self.document_filter, {"$set": {"birthday": birthday.datetime}}
        )

    def to_update_document(self, shutdown=False) -> tuple:
        # self.cache_voice_xp()
        updates = {
            "currency.bosons": self.bosons,
            "stats.xp.chat": self.xp,
            "stats.xp.voice": self._voice_xp,
        }

        if shutdown:
            self.close_voice_activity()

        for profile in self.guild_profiles.values():

            if shutdown:
                profile.close_voice_activity()

            updates.update(profile.to_update_document())

            try:
                _ = profile.guild
            except exceptions.GuildNotFoundError:
                # Case when maybe bot has been removed from the guild. But GuildMemberProfiles still exists in cache.
                # Remove the GuildMemberProfile of this user from the cache.
                self.guild_profiles.pop(profile.id, None)
                # Remove the CosmosGuild from the cache.
                self.plugin.bot.guild_cache.lru.pop(profile.guild_id, None)

        return self.document_filter, {"$set": updates}

    async def get_text_rank(self):
        pipeline = [
            {"$match": {f"stats.xp.chat": {"$gt": self.xp}}}, {"$count": "surpassed"}
        ]
        document = await self.collection.aggregate(pipeline).to_list(None)
        try:
            return document[0]["surpassed"] + 1
        except IndexError:
            return 1

    async def get_voice_rank(self):
        pipeline = [
            {"$match": {f"stats.xp.voice": {"$gt": self._voice_xp}}}, {"$count": "surpassed"}
        ]
        document = await self.collection.aggregate(pipeline).to_list(None)
        try:
            return document[0]["surpassed"] + 1
        except IndexError:
            return 1

    async def get_embed(self):
        # placeholder = "**Guild:** {}\n**Global:** {}"    # TODO
        emotes = self.plugin.bot.emotes.misc
        embed = self.plugin.bot.theme.embeds.primary()
        name = f"    👑    {self.user}" if self.is_prime else self.user
        embed.set_author(name=name, icon_url=self.user.avatar_url)
        embed.description = self.description
        embed.add_field(name=f"{emotes.favorite}    Reputation points", value=self.reps)
        embed.add_field(name=f"{emotes.bank}    Bosons", value=self.bosons)
        embed.add_field(name=f"{emotes.cash}    Fermions", value=self.fermions)
        embed.add_field(name=f"**{emotes.leaderboard} Global Text Rank**", value=f"# **{await self.get_text_rank()}**")
        embed.add_field(name="Text Level", value=self.level)
        embed.add_field(name="Text Experience points", value=self.xp)
        embed.add_field(
            name=f"**{emotes.leaderboard} Global Voice Rank**", value=f"# **{await self.get_voice_rank()}**")
        embed.add_field(name="Voice Level", value=self.voice_level)
        embed.add_field(name="Voice Experience Points", value=self.voice_xp)
        if self.birthday:
            embed.add_field(name=f"{emotes.birthday}    Birthday", value=self.birthday.strftime("%e %B"))
        if self.proposed:
            embed.add_field(name=f"{emotes.two_hearts}    Proposed", value=self.proposed)
        if self.proposer:
            embed.add_field(name=f"{emotes.heart}    Proposer", value=self.proposer)
        if self.spouse_id:
            embed.add_field(name=f"{emotes.ring}    Married with",
                            value=f"{self.spouse}\nMarried {self.marriage_timestamp.humanize()}.")
        # embed.add_field(name="Parents", value=self.parents)
        # embed.add_field(name="Family", value=self.children)
        embed.set_footer(text="Cosmos Profile", icon_url=self.plugin.bot.user.avatar_url)
        return embed

    async def __fetch_guild_profiles(self):
        pass

    async def get_guild_profile(self, guild_id: int) -> GuildMemberProfile:
        if not self.plugin.bot.get_guild(guild_id):
            raise exceptions.GuildNotFoundError(guild_id, self.id)
        profile = self.guild_profiles.get(guild_id)
        if not profile:
            document = await self.collection.find_one(
                self.document_filter, {f"guilds.{guild_id}": ""}
            ) or dict()
            document = document.get("guilds", dict()).get(str(guild_id), dict())
            profile = GuildMemberProfile.from_document(self, guild_id, document)
            self.guild_profiles.set(guild_id, profile)
        return profile
