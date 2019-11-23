class ReactionRole(object):

    def __init__(self, message_id, roles):
        self.message_id = int(message_id)
        self.roles = roles    # [(discord.Role, discord.Emoji), ]


class GuildReactions(object):

    def __init__(self, guild_profile, reactions):
        self.__profile = guild_profile
        self.roles = [
            ReactionRole(
                message_id, self.get_roles_bullets(raw_roles)
            ) for message_id, raw_roles in reactions.get("roles", dict()).items()
        ]

    def get_roles_bullets(self, raw_roles):
        return list(zip(
            [self.__profile.guild.get_role(_) for _ in raw_roles], self.__profile.plugin.bot.emotes.foods.emotes))

    def get_reaction_role(self, message_id):
        try:
            return [_ for _ in self.roles if _.message_id == message_id][0]
        except IndexError:
            pass

    async def add_roles(self, message_id, roles):
        if not (existing_role := self.get_reaction_role(message_id)):
            self.roles.append(ReactionRole(message_id, self.get_roles_bullets(roles)))
        else:
            existing_role.roles = roles
        await self.__profile.collection.update_one(self.__profile.document_filter, {"$set": {
            f"reactions.roles.{message_id}": [role.id for role, _ in roles]
        }})

    async def remove_roles(self, message_id):
        self.roles.remove(self.get_reaction_role(message_id))
        await self.__profile.collection.update_one(self.__profile.document_filter, {"$unset": {
            f"reaction.roles.{message_id}": ""
        }})
