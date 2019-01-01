from .controller.evaluator import Evaluator

__all__ = [Evaluator]


def setup(bot):
    plugin = bot.plugins.get_from_file(__file__)
    plugin.load_cogs(__all__)
