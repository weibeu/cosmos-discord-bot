from .controller.evaluator import Evaluator

__all__ = [Evaluator]


def setup(bot):
    plugin = bot.plugins.get(bot.utilities.get_file_directory(__file__))
    plugin.load_cogs(__all__)
