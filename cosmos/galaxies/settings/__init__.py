from .administrator import AdministratorSettings


__all__ = [
    AdministratorSettings,
]


def setup(bot):
    bot.plugins.setup(__file__)
