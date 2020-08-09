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

from ... import Cog

from cosmos import exceptions
from abc import ABC, abstractmethod


class CosmosGuildBase(ABC):

    @property
    def name(self):
        return self.guild.name

    @property
    @abstractmethod
    def plugin(self):
        raise NotImplementedError

    @property
    def collection(self):
        return self.plugin.collection

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    def guild(self):
        if not (_ := self.plugin.bot.get_guild(self.id)):
            raise exceptions.GuildNotFoundError(self.id)
        return _

    @property
    def document_filter(self):
        return {
            "guild_id": self.id
        }


class GuildBaseCog(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    async def cog_before_invoke(self, ctx):
        ctx.guild_profile = await ctx.fetch_guild_profile()
        # Ensure CosmosGuild is in cache before changing its settings and dynamically pass it to ctx.guild_profile.
