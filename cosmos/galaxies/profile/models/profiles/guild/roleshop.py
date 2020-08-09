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

from .....guild._models.roleshop import Roles


class MemberRoleShop(object):

    def __init__(self, profile, **kwargs):
        self.profile = profile
        raw_roleshop = kwargs.get("roleshop", dict())
        self.roles = Roles()
        self.profile.plugin.bot.loop.create_task(
            self.__fetch_roles(raw_roleshop.get("roles", list())))

    async def __fetch_roles(self, raw_roles):
        roles = (await self.profile.fetch_guild_profile()).roleshop.roles
        self.roles.extend([role for role in roles if role.id in raw_roles])
