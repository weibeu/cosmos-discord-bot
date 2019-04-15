from abc import ABC

from .base import CosmosGuildBase


class RoleShopRole(object):

    def __init__(self, **kwargs):
        self.id = kwargs["role_id"]
        self.points = kwargs["points"]

    @property
    def document(self):
        return {
            "role_id": self.id,
            "points": self.points,
        }


class Roles(list):

    def get(self, role_id):
        for role_document in self:
            if role_document["role_id"] == role_id:
                return RoleShopRole(**role_document)

    def remove(self, role_id):
        super().remove(self.get(role_id))


class RoleShop(object):

    def __init__(self, guild_profile, **kwargs):
        self.__profile = guild_profile
        raw_roleshop = kwargs.get("roleshop", dict())
        self.roles = Roles(raw_roleshop.get("roles", list()))

    async def create_role(self, role_id, points):
        role_document = {
            "role_id": role_id,
            "points": points,
        }
        self.roles.append(role_document)

        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$addToSet": {
                "roleshop.roles": role_document
            }}
        )

    async def remove_role(self, role_id):
        self.roles.remove(role_id)

        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {
                "roleshop.roles": {"role_id": role_id}
            }}
        )


class GuildRoleShop(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        self.roleshop = RoleShop(self, **kwargs)
