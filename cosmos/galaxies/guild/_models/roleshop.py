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
        for role in self:
            if role.id == role_id:
                return role

    def remove(self, role_id):
        super().remove(self.get(role_id))


class RoleShop(object):

    def __init__(self, guild_profile, **kwargs):
        self.__profile = guild_profile
        raw_roleshop = kwargs.get("roleshop", dict())
        self.roles = Roles()
        self.__fetch_roles(raw_roleshop)

    def __fetch_roles(self, raw_roleshop):
        for role_document in raw_roleshop.get("roles", list()):
            self.roles.append(RoleShopRole(**role_document))

    async def create_role(self, role_id, points):
        role = RoleShopRole(role_id=role_id, points=points)
        self.roles.append(role)

        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$addToSet": {
                "roleshop.roles": role.document
            }}
        )

    async def remove_role(self, role_id):
        self.roles.remove(role_id)

        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {
                "roleshop.roles": {"role_id": role_id}
            }}
        )
        # TODO: Remove ^ role data from all users documents who have it.

    async def set_points(self, role_id, points):
        role = self.roles.get(role_id)
        role.points = points

        document_filter = self.__profile.document_filter.copy()
        document_filter.update({"roleshop.roles.role_id": role_id})
        self.__profile.collection.update_one(
            document_filter, {"$set": {
                "roleshop.roles.$.points": role.points
            }}
        )

    def has_role(self, role_id):
        if self.roles.get(role_id):
            return True
        return False


class GuildRoleShop(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        self.roleshop = RoleShop(self, **kwargs)
