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

from abc import ABC

from .exceptions import *
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
        self.__profile_galaxy = self.__profile.plugin.bot.get_galaxy("PROFILE")

    def __bool__(self):
        return bool(self.roles)

    def __fetch_roles(self, raw_roleshop):
        for role_document in raw_roleshop.get("roles", list()):
            self.roles.append(RoleShopRole(**role_document))

    async def create_role(self, role_id, points):
        role = RoleShopRole(role_id=role_id, points=points)
        self.roles.append(role)

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {"roleshop.roles": {"role_id": role.id}}}
        )

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$addToSet": {
                "roleshop.roles": role.document
            }}
        )

    async def remove_role(self, role_id):
        self.roles.remove(role_id)

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {
                "roleshop.roles": {"role_id": role_id}
            }}
        )

        await self.__profile_galaxy.collection.update_many({}, {
            "$pull": {f"guilds.{self.__profile.id}.roleshop.roles": role_id}
        })
        for p in self.__profile_galaxy.cache.lfu.values():
            if profile := p.guild_profiles.get(self.__profile.id):
                try:
                    profile.roleshop.roles.remove(role_id)
                except ValueError:
                    pass

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

    async def buy_role(self, profile, role_id):
        role = self.roles.get(role_id)
        if profile.points < role.points:
            raise NotEnoughPointsError
        profile.roleshop.roles.append(role)
        profile.points -= role.points
        await profile.collection.update_one(profile.document_filter, {
            "$addToSet": {f"{profile.guild_filter}.roleshop.roles": role.id}
        })

    async def sell_role(self, profile, role_id):
        role = self.roles.get(role_id)
        result = await profile.collection.update_one(profile.document_filter, {
            "$pull": {f"{profile.guild_filter}.roleshop.roles": role.id}
        })
        if not result.modified_count:
            raise RoleNotFoundError
        profile.roleshop.roles.remove(role)
        profile.points += role.points

    def has_role(self, role_id):
        if self.roles.get(role_id):
            return True
        return False


class GuildRoleShop(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        self.roleshop = RoleShop(self, **kwargs)
