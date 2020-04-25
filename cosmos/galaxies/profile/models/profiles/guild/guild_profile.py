from .roleshop import MemberRoleShop
from .guild_points import GuildPoints
from .experience import MemberExperience


class GuildMemberProfile(GuildPoints, MemberExperience):

    @property
    def profile(self):
        return self._profile

    @property
    def guild_id(self):
        return self._guild_id

    async def fetch_guild_profile(self):
        return await self.plugin.bot.guild_cache.get_profile(self.guild.id)

    @classmethod
    def from_document(cls, profile, guild_id, document: dict):
        return cls(profile, guild_id, **document)

    def __init__(self, profile, guild_id, **kwargs):
        self._profile = profile    # CosmosUserProfile
        GuildPoints.__init__(self, **kwargs)
        MemberExperience.__init__(self, **kwargs)
        self._guild_id = guild_id
        self.roleshop = MemberRoleShop(self, **kwargs)
        self.moderation_logs = kwargs.get("logs", dict()).get("moderation", list())

    def to_update_document(self):
        self.cache_voice_xp()
        return {
            f"{self.guild_filter}.stats.xp.chat": self.xp,
            f"{self.guild_filter}.stats.xp.voice": self._voice_xp,
            f"{self.guild_filter}.points.points": self.points,
        }

    async def log_moderation(self, _id):
        self.moderation_logs.append(_id)

        await self.collection.update_one(self.document_filter, {
            "$addToSet": {f"{self.guild_filter}.logs.moderation": _id}
        })

    async def clear_moderation_logs(self):
        self.moderation_logs.clear()

        await self.collection.update_one(self.document_filter, {
            "$unset": {f"{self.guild_filter}.logs.moderation": ""}
        })

    async def get_text_rank(self):
        pipeline = [
            {"$match": {
                self.guild_filter: {"$exists": True},
                f"{self.guild_filter}.stats.xp.chat": {"$gt": self.xp}
            }},
            {"$count": "surpassed"}
        ]
        document = await self.collection.aggregate(pipeline).to_list(None)
        try:
            return document[0]["surpassed"] + 1
        except IndexError:
            return 1

    async def get_voice_rank(self):
        pipeline = [
            {"$match": {
                self.guild_filter: {"$exists": True},
                f"{self.guild_filter}.stats.xp.voice": {"$gt": self._voice_xp}
            }},
            {"$count": "surpassed"}
        ]
        document = await self.collection.aggregate(pipeline).to_list(None)
        try:
            return document[0]["surpassed"] + 1
        except IndexError:
            return 1
