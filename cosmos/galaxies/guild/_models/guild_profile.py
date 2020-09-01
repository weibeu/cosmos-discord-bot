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

from .levels import Levels
from .prime import CosmosGuildPrime
from .settings import GuildSettings
from .roleshop import GuildRoleShop
from .reactions import GuildReactions


class CosmosGuild(CosmosGuildPrime, GuildSettings, GuildRoleShop):

    @property
    def plugin(self):
        return self._plugin

    @property
    def id(self):
        return self.__id

    @classmethod
    def from_document(cls, plugin, document: dict):
        return cls(plugin, **document)

    async def fetch_member_profile(self, _id):
        return await self.plugin.bot.profile_cache.get_guild_profile(_id, self.id)

    def __init__(self, plugin, **kwargs):
        self._plugin = plugin
        self.__id = kwargs["guild_id"]
        CosmosGuildPrime.__init__(self, **kwargs)
        GuildSettings.__init__(self, **kwargs)
        GuildRoleShop.__init__(self, **kwargs)
        self.levels = Levels(self, **kwargs)
        self.reactions = GuildReactions(self, kwargs.get("reactions", dict()))
