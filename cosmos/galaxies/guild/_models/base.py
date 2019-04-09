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
