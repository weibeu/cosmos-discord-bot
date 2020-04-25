from cosmos import exceptions
from abc import ABC

import arrow

from .tags import UserTags
from .family import Relationship
from .currency import Boson, Fermion

from ..guild import GuildMemberProfile, UserExperience


class CosmosUserProfile(Boson, Fermion, UserExperience, Relationship, UserTags, ABC):

    @property
    def plugin(self):
        return self.__plugin

    @property
    def collection(self):
        return self.__collection

    @property
    def id(self):
        return self._id

    @property
    def is_prime(self):
        return self._is_prime

    @is_prime.setter
    def is_prime(self, value):
        self._is_prime = value

    @property
    def description(self):
        return self._description or self.plugin.data.profile.default_description

    @classmethod
    def from_document(cls, plugin, document: dict):
        return cls(plugin, **document)

    def __init__(self, plugin, **kwargs):
        Boson.__init__(self, **kwargs)
        Fermion.__init__(self, **kwargs)
        UserExperience.__init__(self, **kwargs)
        Relationship.__init__(self, **kwargs)
        UserTags.__init__(self, kwargs.get("tags", dict()))
        self.__plugin = plugin
        self._id: int = kwargs["user_id"]
        self._is_prime = kwargs.get("is_prime", False)
        raw_reputation = kwargs.get("reputation", dict())
        self.reps: int = raw_reputation.get("points", 0)
        self.rep_timestamp = self.get_arrow(raw_reputation.get("timestamp"))
        # self.badges = []
        self._description: str = kwargs.get("description", str())
        self.birthday = self.get_arrow(kwargs.get("birthday"))
        self.rank = None
        # self.inventory = []
        # self.on_time: int = None
        self.guild_profiles = self.plugin.bot.cache.lfu(self.plugin.data.profile.guild_profiles_cache_max_size)
        self.__collection = self.plugin.collection
        if self.plugin.data.profile.fetch_guild_profiles:
            self.plugin.bot.create_task(self.__fetch_guild_profiles())    # TODO: Fetch profiles of all guilds.

    async def make_prime(self, make=True):
        self.is_prime = make

        await self.collection.update_one(
            self.document_filter, {"$set": {"is_prime": make}})

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
            birthday = arrow.get(birthday)
        self.birthday = birthday

        await self.collection.update_one(
            self.document_filter, {"$set": {"birthday": birthday.datetime}}
        )

    def to_update_document(self) -> tuple:
        self.cache_voice_xp()
        updates = {
            "currency.bosons": self.bosons,
            "stats.xp.chat": self.xp,
            "stats.xp.voice": self._voice_xp,
        }

        for profile in self.guild_profiles.values():
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
        profile = self.guild_profiles.get(guild_id)
        if not profile:
            document = await self.collection.find_one(
                self.document_filter, {f"guilds.{guild_id}": ""}
            ) or dict()
            document = document.get("guilds", dict()).get(str(guild_id), dict())
            profile = GuildMemberProfile.from_document(self, guild_id, document)
            self.guild_profiles.set(guild_id, profile)
        return profile
