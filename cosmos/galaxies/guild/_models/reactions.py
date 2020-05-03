class ReactionRole(object):

    def __init__(self, message_id, roles, stack=True):
        self.message_id = message_id
        self.roles = roles
        self.stack = stack

    @property
    def document(self):
        return dict(message_id=self.message_id, roles=[role.id for role in self.roles], stack=self.stack)


class GuildReactions(object):

    def __init__(self, guild_profile, reactions):
        self.__profile = guild_profile
        self.roles = {
            document["message_id"]: ReactionRole(document["message_id"], [
                self.__profile.guild.get_role(_) for _ in document["roles"]
            ], document.get("stack", True)) for document in reactions.get("roles", list())}

    async def __pull_document(self, message_id):
        await self.__profile.collection.update_one(self.__profile.document_filter, {"$pull": {
            "reactions.roles": {"message_id": message_id}}})

    async def add_roles(self, message_id, roles, stack=True):
        rr = ReactionRole(message_id, roles, stack)
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
