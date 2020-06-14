from .tags import Tags
from .imgur import Imgur
from .hastebin import HasteBin
from .utilitiies import Utilities


__all__ = [
    Tags,
    Imgur,
    HasteBin,
    Utilities,
]


def setup(bot):
    bot.plugins.setup(__file__)
