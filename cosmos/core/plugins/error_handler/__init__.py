from ._bot import BotErrorHandler
from .command import CommandErrorHandler


__all__ = [BotErrorHandler, CommandErrorHandler]


def setup(bot):
    bot.plugins.setup(__file__)
