from .logger import Logger
from .moderation import Moderation
from .automoderation import AutoModeration
from .verification import UserVerification


__all__ = [
    Logger,
    Moderation,
    AutoModeration,
    UserVerification,
]


def setup(bot):
    bot.plugins.setup(__file__, INESCAPABLE=False)
