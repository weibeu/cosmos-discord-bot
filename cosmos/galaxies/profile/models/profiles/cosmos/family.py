from abc import ABC

import arrow

from ..base import ProfileModelsBase


class Marriage(ProfileModelsBase, ABC):

    def __init__(self, marriage_document):
        self.proposed_id = marriage_document.get("proposed")
        self.proposer_id = marriage_document.get("proposer")
        self.spouse_id = marriage_document.get("spouse")
        self.marriage_timestamp = self.get_arrow(marriage_document.get("timestamp"))

    # Return discord.User instead of CosmosUserProfile because it would summon three more users to cache.

    @property
    def proposed(self):
        return self.plugin.bot.get_user(self.proposed_id)

    @property
    def proposer(self):
        return self.plugin.bot.get_user(self.proposer_id)

    @property
    def spouse(self):
        return self.plugin.bot.get_user(self.spouse_id)

    async def propose(self, author_profile):
        self.proposer_id = author_profile.id
        author_profile.proposed_id = self.id

        await self.collection.update_one(
            self.document_filter, {"$set": {"relationship.marriage.proposer": self.proposer_id}}
        )
        await self.collection.update_one(
            author_profile.document_filter, {"$set": {"relationship.marriage.proposed": author_profile.proposed_id}}
        )

    async def decline_proposal(self, target_profile):
        self.proposer_id = None
        target_profile.proposed_id = None

        await self.collection.update_one(
            self.document_filter, {"$unset": {"relationship.marriage.proposer": ""}}
        )
        await self.collection.update_one(
            target_profile.document_filter, {"$unset": {"relationship.marriage.proposed": ""}}
        )

    async def cancel_proposal(self, target_profile):
        self.proposed_id = None
        target_profile.proposer_id = None

        await self.collection.update_one(
            self.document_filter, {"$unset": {"relationship.marriage.proposed": ""}}
        )
        await self.collection.update_one(
            target_profile.document_filter, {"$unset": {"relationship.marriage.proposer": ""}}
        )

    async def marry(self, author_profile):
        self.spouse_id = author_profile.id
        self.marriage_timestamp = arrow.utcnow()
        author_profile.spouse_id = self.id
        author_profile.marriage_timestamp = self.marriage_timestamp

        await self.collection.update_one(
            self.document_filter, {
                "$set": {
                    "relationship.marriage.spouse": self.spouse_id,
                    "relationship.marriage.timestamp": self.marriage_timestamp.datetime
                }
            }
        )
        await self.collection.update_one(
            author_profile.document_filter, {
                "$set": {
                    "relationship.marriage.spouse": author_profile.spouse_id,
                    "relationship.marriage.timestamp": author_profile.marriage_timestamp.datetime
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

        await self.collection.update_one(
            self.document_filter, {"$unset": {"relationship.marriage": ""}}
        )
        await self.collection.update_one(
            target_profile.document_filter, {"$unset": {"relationship.marriage": ""}}
        )


class Relationship(Marriage, ABC):

    def __init__(self, **kwargs):
        relationship_document = kwargs.get("relationship", dict())
        super().__init__(relationship_document.get("marriage", dict()))
        self._parents = relationship_document.get("parents", list())
        self._children = relationship_document.get("children", list())

    @property
    def children(self):
        return [self.plugin.bot.get_user(child_id) for child_id in self._children]

    @property
    def parents(self):
        return [self.plugin.bot.get_user(parent_id) for parent_id in self._parents]

    async def adopt(self, target_profile):
        self._children.append(target_profile.id)
        # TODO: Handle same children for two profiles.
