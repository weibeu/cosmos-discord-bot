from .commands import AdminCommands
from .controller.evaluator import Evaluator


__all__ = [
    Evaluator,
    AdminCommands,
]


def setup(bot):
    bot.plugins.setup(__file__)
