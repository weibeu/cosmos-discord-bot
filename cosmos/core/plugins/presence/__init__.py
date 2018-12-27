from .presence import Presence

cogs = [Presence]


def setup(bot):
    plugin = bot.plugins.get(bot.utilities.get_file_directory(__file__))
    # plugin.load_cogs(cogs)
