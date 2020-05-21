from .tags import Tags
from .hastebin import HasteBin
from .utilitiies import Utilities


__all__ = [
    Tags,
    HasteBin,
    Utilities,
]


def setup(bot):
    bot.plugins.setup(__file__)
