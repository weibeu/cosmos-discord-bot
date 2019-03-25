from abc import ABC, abstractmethod


class CosmosGuildBase(ABC):

    # @property
    # @abstractmethod
    # def plugin(self):
    #     raise NotImplementedError
    #
    # @property
    # @abstractmethod
    # def collection(self):
    #     raise NotImplementedError

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    # @property
    # def guild(self):
    #     return self.plugin.bot.get_guild(self.id)
    #
    # @property
    # def document_filter(self):
    #     return {
    #         "guild_id": self.id
    #     }
