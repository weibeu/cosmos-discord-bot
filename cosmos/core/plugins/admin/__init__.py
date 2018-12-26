from .controller.evaluator import Evaluator


def setup(bot):
    plugin = bot.plugins.get(bot.utilities.get_file_directory(__file__))
    bot.add_cog(Evaluator(plugin))
