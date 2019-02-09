from .profile import Profile
from .economy import Economy
from .ascension import Levels
from .models import ProfileCache

__all__ = [
    Profile,
    Levels,
    Economy
]


def setup(bot):
    plugin = bot.plugins.setup(__file__)
    plugin.cache = ProfileCache(plugin)
