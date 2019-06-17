from .logger import Logger
from .moderation import Moderation
from .automoderation import AutoModeration


__all__ = [
    Logger,
    Moderation,
    AutoModeration,
]


def setup(bot):
    bot.plugins.setup(__file__)
