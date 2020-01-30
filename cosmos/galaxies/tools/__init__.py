from .tags import Tags
from .hastebin import HasteBin


__all__ = [
    Tags,
    HasteBin,
]


def setup(bot):
    bot.plugins.setup(__file__)
