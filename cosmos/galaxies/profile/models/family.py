from abc import ABC

import arrow

from .base import ProfileModelsBase


class CosmosMarriage(ProfileModelsBase, ABC):

    def __init__(self, **kwargs):
        raw_marriage = kwargs.get("marriage", dict())
        self.proposed_id = raw_marriage.get("proposed")
        self.proposer_id = raw_marriage.get("proposer")
        self.spouse_id = raw_marriage.get("spouse")
        self.marriage_timestamp = self.get_arrow(raw_marriage.get("timestamp"))

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

    async def propose(self, author_profile):
        self.proposer_id = author_profile.id
        author_profile.proposed_id = self.id

        await self._collection.update_one(
            {"user_id": self.id}, {"$set": {"marriage.proposer": self.proposer_id}}
        )
        await self._collection.update_one(
            {"user_id": author_profile.id}, {"$set": {"marriage.proposed": author_profile.proposed_id}}
        )

    async def decline_proposal(self, target_profile):
        self.proposer_id = None
        target_profile.proposed_id = None

        await self._collection.update_one(
            {"user_id": self.id}, {"$unset": {"marriage.proposer": "$"}}
        )
        await self._collection.update_one(
            {"user_id": target_profile.id}, {"$unset": {"marriage.proposed": "$"}}
        )

    async def cancel_proposal(self, target_profile):
        self.proposed_id = None
        target_profile.proposer_id = None

        await self._collection.update_one(
            {"user_id": self.id}, {"$unset": {"marriage.proposed": "$"}}
        )
        await self._collection.update_one(
            {"user_id": target_profile.id}, {"$unset": {"marriage.proposer": "$"}}
        )

    async def marry(self, author_profile):
        self.spouse_id = author_profile.id
        self.marriage_timestamp = arrow.utcnow()
        author_profile.spouse_id = self.id
        author_profile.marriage_timestamp = self.marriage_timestamp

        await self._collection.update_one(
            self.document_filter, {
                "$set": {"marriage.spouse": self.spouse_id, "marriage.timestamp": self.marriage_timestamp.datetime}
            }
        )
        await self._collection.update_one(
            author_profile.document_filter, {
                "$set": {
                    "marriage.spouse": author_profile.spouse_id,
                    "marriage.timestamp": author_profile.marriage_timestamp.datetime
                }
            }
        )

    async def divorce(self, target_profile):
        self.spouse_id = None
        self.proposer_id = None
        self.proposed_id = None
        target_profile.spouse_id = None
        target_profile.proposed_id = None
        target_profile.proposer_id = None

        await self._collection.update_one(
            {"user_id": self.id}, {"$unset": {"marriage": "$"}}
        )
        await self._collection.update_one(
            {"user_id": target_profile.id}, {"$unset": {"marriage": "$"}}
        )
