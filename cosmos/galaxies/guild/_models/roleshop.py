from abc import ABC

from .base import CosmosGuildBase


class RoleShopRole(object):

    def __init__(self):
        pass


class RoleShop(object):

    def __init__(self, **kwargs):
        raw_roleshop = kwargs["roleshop"]
        self.__raw_roles = raw_roleshop.get("roles", dict())

    def __len__(self):
        return len(self.__raw_roles)


class GuildRoleShop(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        if kwargs.get("roleshop"):
            self.roleshop = RoleShop()
