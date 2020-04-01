from .levels import Levels
from ._models import GuildCache
from .roleshop import RoleShop
from .reactor import Reactor
from .welcome import Welcome
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
