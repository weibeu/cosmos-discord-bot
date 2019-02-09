from .profile import Profile
from .economy import Economy
from .ascension import Levels
from .marriage import Marriage

from .models import ProfileCache

__all__ = [
    Profile,
    Levels,
    Economy,
    Marriage
]


def setup(bot):
    bot.plugins.setup(__file__, cache=ProfileCache)    # setup method automatically passes plugin.
