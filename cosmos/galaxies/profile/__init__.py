from .profile import Profile
from .economy import Economy
from .ascension.levels import Levels

__all__ = [
    Profile,
    Levels,
    Economy
]


def setup(bot):
    bot.plugins.setup(__file__)
