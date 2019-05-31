from .logger import Logger


__all__ = [
    Logger,
]


def setup(bot):
    bot.plugins.setup(__file__)
