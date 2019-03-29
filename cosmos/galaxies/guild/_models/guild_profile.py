from .settings import GuildSettings


class CosmosGuild(GuildSettings):

    # @property
    # def plugin(self):
    #     return self.__plugin
    #
    # @property
    # def collection(self):
    #     pass

    @property
    def id(self):
        return self.__id

    @classmethod
    def from_document(cls, document: dict):
        return cls(**document)

    def __init__(self, **kwargs):
        self.__id = kwargs["guild_id"]
        self.is_prime = kwargs.get("is_prime", False)
        GuildSettings.__init__(self, **kwargs)
