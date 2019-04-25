from .guild_points import GuildPoints


class GuildMemberProfile(GuildPoints):

    @property
    def profile(self):
        return self._profile

    @property
    def guild(self):
        return self.profile.plugin.bot.get_guild(self._guild_id)

    @classmethod
    def from_document(cls, profile, guild_id, document: dict):
        return cls(profile, guild_id, **document)

    def __init__(self, profile, guild_id, **kwargs):
        self._profile = profile    # CosmosUserProfile
        GuildPoints.__init__(self, **kwargs)
        self._guild_id = guild_id

    def to_update_document(self):
        return {
            f"{self.guild_filter}.points.points": self.points,
        }
