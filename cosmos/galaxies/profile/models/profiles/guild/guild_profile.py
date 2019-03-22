from .guild_points import GuildPoints


class GuildMemberProfile(GuildPoints):

    @property
    def profile(self):
        return self._profile

    @property
    def guild_id(self):
        return self._guild_id

    @classmethod
    def from_document(cls, profile, **document: dict):
        return cls(profile, **document)

    def __init__(self, profile, guild_id, **kwargs):
        self._profile = profile    # CosmosUserProfile
        GuildPoints.__init__(self, **kwargs)
        self._guild_id = guild_id
