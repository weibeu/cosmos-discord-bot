from .information import CosmosInformation


__all__ = [
    CosmosInformation,
]


def setup(bot):
    bot.plugins.setup(__file__)
