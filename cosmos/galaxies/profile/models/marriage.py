from abc import ABC
from .base import ProfileModelsBase


class CosmosMarriage(ProfileModelsBase, ABC):

    def __init__(self, **kwargs):
        raw_marriage = kwargs.get("marriage", dict())
        self.proposed_id = raw_marriage.get("proposed")
        self.proposer_id = raw_marriage.get("proposer")
        self.spouse_id = raw_marriage.get("spouse")

    # Return discord.User instead of CosmosUserProfile because it would summon three more users to cache.

    @property
    def proposed(self):
        return self._plugin.bot.get_user(self.proposed_id)

    @property
    def proposer(self):
        return self._plugin.bot.get_user(self.proposer_id)

    @property
    def spouse(self):
        return self._plugin.bot.get_user(self.spouse_id)
