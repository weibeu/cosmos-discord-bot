from .tags import Tags


__all__ = [
    Tags,
]


def setup(bot):
    bot.plugins.setup(__file__)
