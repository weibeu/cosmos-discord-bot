"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

class ReactionRole(object):

    def __init__(self, message_id, roles, stack=True, permanent=False):
        self.message_id = message_id
        self.roles = roles
        self.stack = stack
        self.permanent = permanent

    @property
    def document(self):
        return dict(
            message_id=self.message_id, roles=[role.id for role in self.roles], stack=self.stack,
            permanent=self.permanent)


class GuildReactions(object):

    def __init__(self, guild_profile, reactions):
        self.__profile = guild_profile
        self.roles = {
            document["message_id"]: ReactionRole(
                document["message_id"], [self.__profile.guild.get_role(_) for _ in document["roles"]],
                document.get("stack", True), document.get("permanent", False)
            ) for document in reactions.get("roles", list())}

    async def __pull_document(self, message_id):
        await self.__profile.collection.update_one(self.__profile.document_filter, {"$pull": {
            "reactions.roles": {"message_id": message_id}}})

    async def add_roles(self, message_id, roles, stack=True, permanent=False):
        rr = ReactionRole(message_id, roles, stack, permanent)
        self.roles.update({message_id: rr})

        await self.__pull_document(rr.message_id)
        await self.__profile.collection.update_one(self.__profile.document_filter, {"$addToSet": {
            f"reactions.roles": rr.document}})

    async def remove_roles(self, message_id):
        self.roles.pop(message_id, None)
        await self.__pull_document(message_id)

    async def remove_all_reaction_roles(self):
        self.roles = dict()
        await self.__profile.collection.update_one(self.__profile.document_filter, {"$unset": {"reactions.roles": ""}})
