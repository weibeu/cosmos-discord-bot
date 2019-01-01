from ._bot import BotErrorHandler
from .command import CommandErrorHandler


__all__ = [BotErrorHandler, CommandErrorHandler]


def setup(bot):
    plugin = bot.plugins.get_from_file(__file__)
    plugin.load_cogs(__all__)
