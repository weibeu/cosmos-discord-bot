from .profile import Profile
from .economy import Economy
from .ascension import _Levels
from .marriage import Marriage
from .leaderboards import Leaderboards

from .models import ProfileCache

__all__ = [
    Profile,
    _Levels,
    Economy,
    Marriage,
    Leaderboards,
]


def setup(bot):
    # plugin = bot.plugins.setup(__file__, cache=ProfileCache)    # setup method automatically passes plugin.
    plugin = bot.plugins.get_from_file(__file__)
    plugin.collection = bot.db[plugin.data.profile.collection_name]
    plugin.batch = bot.db_client.batch(plugin.collection)
    plugin.cache = ProfileCache(plugin)

    plugin.load_cogs(__all__)

    bot.profile_cache = plugin.cache
