from .users import UsersCustomCommands


__all__ = [
    UsersCustomCommands,
]


def setup(bot):
    bot.plugins.setup(__file__)
