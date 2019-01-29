from .ascension.levels import Levels

__all__ = [
    Levels
]


def setup(bot):
    bot.plugins.setup(__file__)
