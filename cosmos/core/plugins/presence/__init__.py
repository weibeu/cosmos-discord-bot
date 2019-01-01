from .presence import Presence

__all__ = [Presence]    # Fast.


def setup(bot):
    # plugin = bot.plugins.get_from_file(__file__)
    # plugin.load_cogs(__all__)    # Slow.
    # or
    # plugin.load_cogs([Presence])
    # bot.plugins.setup(__file__, __all__)    # Fast.
    bot.plugins.setup(__file__)    # Shorthand. Slow.
