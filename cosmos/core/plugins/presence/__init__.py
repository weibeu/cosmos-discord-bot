from .presence import Presence

__all__ = [Presence]


def setup(bot):
    plugin = bot.plugins.get_from_file(__file__)
    plugin.load_cogs(__all__)
