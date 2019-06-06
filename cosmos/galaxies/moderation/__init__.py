from .logger import Logger
from .moderation import Moderation


__all__ = [
    Logger,
    Moderation,
]


def setup(bot):
    bot.plugins.setup(__file__)
