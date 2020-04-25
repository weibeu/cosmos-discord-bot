from ..base import ProfileModelsBase

from cosmos import exceptions
from abc import abstractmethod


class GuildMemberProfileBase(ProfileModelsBase):

    def __str__(self):
        return self.member.__str__()

    # TODO: Add a special dunder method which returns attribute from self.member if its not found in self.

    @property
    @abstractmethod
    def profile(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def guild_id(self):
        raise NotImplementedError

    @property
    def guild(self):
        if not (_ := self.profile.plugin.bot.get_guild(self.guild_id)):
            raise exceptions.GuildNotFoundError(self.guild_id, self.id)
        return _

    @abstractmethod
    async def fetch_guild_profile(self):
        raise NotImplementedError

    @property
    def member(self):
        return self.guild.get_member(self.id)

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
        return f"guilds.{self.guild_id}"
