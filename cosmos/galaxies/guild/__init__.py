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
from ._models import GuildCache
from .roleshop import RoleShop
from .reactor import Reactor
from .welcome import Welcome
from .giveaway import Giveaway
from .starboard import Starboard
from .reactions import ReactionRoles
from .settings import GuildSettings
from .confessions import SecretConfessions
from .permissions import CosmosPermissions


__all__ = [
    Levels,
    RoleShop,
    Reactor,
    Welcome,
    Starboard,
    Giveaway,
    ReactionRoles,
    GuildSettings,
    SecretConfessions,
    CosmosPermissions,
]


def setup(bot):
    plugin = bot.plugins.get_from_file(__file__)
    plugin.collection = bot.db[plugin.data.guild.collection_name]
    plugin.cache = GuildCache(plugin)
    plugin.INESCAPABLE = False

    plugin.load_cogs(__all__)

    bot.guild_cache = plugin.cache
