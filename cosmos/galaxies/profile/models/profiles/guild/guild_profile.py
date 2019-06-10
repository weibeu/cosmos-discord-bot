from .roleshop import MemberRoleShop
from .guild_points import GuildPoints
from .experience import UserExperience


class GuildMemberProfile(GuildPoints, UserExperience):

    @property
    def profile(self):
        return self._profile

    @property
    def guild(self):
        return self.profile.plugin.bot.get_guild(self._guild_id)

    async def fetch_guild_profile(self):
        return await self.plugin.bot.guild_cache.get_profile(self.guild.id)

    @classmethod
    def from_document(cls, profile, guild_id, document: dict):
        return cls(profile, guild_id, **document)

    def __init__(self, profile, guild_id, **kwargs):
        self._profile = profile    # CosmosUserProfile
        GuildPoints.__init__(self, **kwargs)
        UserExperience.__init__(self, **kwargs)
        self._guild_id = guild_id
        self.roleshop = MemberRoleShop(self, **kwargs)
        self.moderation_logs = kwargs.get("warnings", list())

    def to_update_document(self):
        return {
            f"{self.guild_filter}.stats.xp.chat": self.xp,
            f"{self.guild_filter}.stats.xp.voice": self.voice_xp,
            f"{self.guild_filter}.stats.level.chat": self.level,
            f"{self.guild_filter}.points.points": self.points,
        }

    async def add_warning(self, _id):
        self.moderation_logs.append(_id)

        await self.collection.update_one(self.document_filter, {
            "$addToSet": {f"{self.guild_filter}.logs.moderation": _id}
        })

    async def clear_warnings(self):
        self.moderation_logs.clear()
