from .primary import Primary
from .one_line import OneLine


class CosmosEmbed(object):

    def __init__(self, bot):
        self.bot = bot
        self.primary_color = self.bot.configs.color_scheme.primary

    def primary(self, **kwargs):
        return Primary(self.bot, **kwargs)

    def one_line(self, content: str, emote: str = str(), **kwargs):
        return OneLine(self.bot, emote, content, **kwargs)


__all__ = [
    "CosmosEmbed"
]
