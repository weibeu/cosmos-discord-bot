from ... import Cog

from abc import ABC, abstractmethod


class CosmosGuildBase(ABC):

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
        return self.plugin.bot.get_guild(self.id)

    @property
    def document_filter(self):
        return {
            "guild_id": self.id
        }


class GuildBaseCog(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def cog_before_invoke(self, ctx):
        ctx.guild_profile = await ctx.fetch_guild_profile()
        # Ensure CosmosGuild is in cache before changing its settings and dynamically pass it to ctx.guild_profile.
