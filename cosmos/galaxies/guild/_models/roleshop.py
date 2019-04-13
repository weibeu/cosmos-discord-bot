from abc import ABC

from .base import CosmosGuildBase


class RoleShopRole(object):

    def __init__(self, **kwargs):
        self.points = kwargs["points"]


class RoleShop(object):

    def __init__(self, guild_profile, **kwargs):
        self.__profile = guild_profile
        raw_roleshop = kwargs.get("roleshop", dict())
        self.__raw_roles = raw_roleshop.get("roles", dict())

    async def create_role(self, role_id, points,):
        raw_role = {
            "points": points,
            # "prime": True,
        }
        self.__raw_roles.update({role_id: raw_role})

        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$set": {
                f"roleshop.roles.{role_id}.points": points,
                # f"roleshop.roles.{role_id}.prime": True,
            }}
        )


class GuildRoleShop(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        self.roleshop = RoleShop(self, **kwargs)
