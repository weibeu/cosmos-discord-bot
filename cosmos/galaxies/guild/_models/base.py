from ... import Cog

from cosmos import exceptions
from abc import ABC, abstractmethod


class CosmosGuildBase(ABC):

    @property
    def name(self):
        return self.guild.name

    @property
    @abstractmethod
    def plugin(self):
        raise NotImplementedError

    @property
    def collection(self):
        return self.plugin.collection

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    def guild(self):
        if not (_ := self.plugin.bot.get_guild(self.id)):
            raise exceptions.GuildNotFoundError(self.id)
        return _

    @property
    def document_filter(self):
        return {
            "guild_id": self.id
        }


class GuildBaseCog(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    async def cog_before_invoke(self, ctx):
        ctx.guild_profile = await ctx.fetch_guild_profile()
        # Ensure CosmosGuild is in cache before changing its settings and dynamically pass it to ctx.guild_profile.
