from .primary import Primary
from .one_line import OneLine


class CosmosEmbed(object):

    def __init__(self, bot):
        self.bot = bot
        self.one_line = OneLine(self.bot)

    def primary(self, **kwargs):
        return Primary(self.bot, **kwargs)


__all__ = [
    "CosmosEmbed"
]
