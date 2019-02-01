from .profile import Profile
from .ascension.levels import Levels

__all__ = [
    Profile,
    Levels
]


def setup(bot):
    bot.plugins.setup(__file__)
