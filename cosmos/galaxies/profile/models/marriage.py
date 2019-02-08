from abc import ABC
from .base import ProfileModelsBase


class CosmosMarriage(ProfileModelsBase, ABC):

    def __init__(self, **kwargs):
        self.proposed = None
        self.proposer = None
        self.spouse = None

    async def __fetch_marriage(self, **kwargs):
        raw_marriage = kwargs.get("marriage", dict())
        proposed_id = raw_marriage.get("proposed")
        proposer_id = raw_marriage.get("proposer")
        spouse_id = raw_marriage.get("spouse")
        if proposed_id:
            self.proposed = await self._plugin.profile_cache.get_profile(proposed_id)
        if proposer_id:
            self.proposer = await self._plugin.profile_cache.get_profile(proposer_id)
        if spouse_id:
            self.spouse = await self._plugin.profile_cache.get_profile(spouse_id)
