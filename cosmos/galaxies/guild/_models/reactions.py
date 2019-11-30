class GuildReactions(object):

    def __init__(self, guild_profile, reactions):
        self.__profile = guild_profile
        self.roles = {
            int(message_id): [
                self.__profile.guild.get_role(_) for _ in roles
            ] for message_id, roles in reactions.get("roles", dict()).items()
        }

    async def add_roles(self, message_id, roles):
        self.roles.update({message_id: roles})
        await self.__profile.collection.update_one(self.__profile.document_filter, {"$set": {
            f"reactions.roles.{message_id}": [role.id for role in roles]
        }})

    async def remove_roles(self, message_id):
        self.roles.pop(message_id, None)
        await self.__profile.collection.update_one(self.__profile.document_filter, {"$unset": {
            f"reactions.roles.{message_id}": ""
        }})
