from abc import ABC

from .base import CosmosGuildBase


class RoleShopRole(object):

    def __init__(self, role_id, **kwargs):
        self.id = role_id
        self.points = kwargs["points"]


class Roles(dict):

    def get(self, role_id):
        return RoleShopRole(role_id, **super().get(str(role_id)))

    def set(self, role_id, **kwargs):
        raw = super().get(str(role_id), dict())
        raw.update(kwargs)
        self.update({str(role_id): raw})

    def __iter__(self):
        for key in super().__iter__():
            yield int(key)


class RoleShop(object):

    def __init__(self, guild_profile, **kwargs):
        self.__profile = guild_profile
        raw_roleshop = kwargs.get("roleshop", dict())
        self.roles = Roles(raw_roleshop.get("roles", dict()))

    async def create_role(self, role_id, points,):
        self.roles.set(role_id, points=points)

        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$set": {
                f"roleshop.roles.{role_id}.points": points,
                # f"roleshop.roles.{role_id}.prime": True,
            }}
        )


class GuildRoleShop(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        self.roleshop = RoleShop(self, **kwargs)
