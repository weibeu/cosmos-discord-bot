from .memes import DeadMemes


__all__ = [
    DeadMemes,
]


def setup(bot):
    bot.plugins.setup(__file__)
