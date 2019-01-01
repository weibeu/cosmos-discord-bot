from .controller.evaluator import Evaluator

__all__ = [Evaluator]


def setup(bot):
    bot.plugins.setup(__file__)
