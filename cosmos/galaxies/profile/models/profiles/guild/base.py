from abc import abstractmethod

from ..base import ProfileModelsBase


class GuildProfileModelsBase(ProfileModelsBase):

    @property
    @abstractmethod
    def profile(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def guild(self):
        raise NotImplementedError

    @property
    def plugin(self):
        return self.profile.plugin

    @property
    def collection(self):
        return self.profile.collection

    @property
    def id(self):
        return self.profile.id

    @property
    def is_prime(self):
        return self.profile.is_prime

    @property
    def guild_filter(self):
        return f"guilds.{self.guild.id}"
