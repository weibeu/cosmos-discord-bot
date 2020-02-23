from .levels import Levels
from .settings import GuildSettings
from .roleshop import GuildRoleShop
from .reactions import GuildReactions


class CosmosGuild(GuildSettings, GuildRoleShop):

    @property
    def plugin(self):
        return self.__plugin

    @property
    def id(self):
        return self.__id

    @classmethod
    def from_document(cls, plugin, document: dict):
        return cls(plugin, **document)

    async def fetch_member_profile(self, _id):
        return await self.plugin.bot.profile_cache.get_guild_profile(_id, self.id)

    def __init__(self, plugin, **kwargs):
        self.__plugin = plugin
        self.__id = kwargs["guild_id"]
        self.is_prime = kwargs.get("is_prime", False)
        GuildSettings.__init__(self, **kwargs)
        GuildRoleShop.__init__(self, **kwargs)
        self.levels = Levels(self, **kwargs)
        self.reactions = GuildReactions(self, kwargs.get("reactions", dict()))
