from .presence import Presence

__all__ = [Presence]


def setup(bot):
    plugin = bot.plugins.get(bot.utilities.get_file_directory(__file__))
    plugin.load_cogs(__all__)
