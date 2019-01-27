from .primary import Primary


class OneLinePrimary(Primary):

    def __init__(self, bot, content: str = None, emote: str = str(), color=None, **kwargs):
        self._bot = bot
        if emote:
            content = f"{emote}    {content}"
        assert len(content) <= 256, "Content should be less than or equal to 256 in length."
        super().__init__(title=content, color=color, **kwargs)

    @property
    def bot(self):
        return self._bot


class OneLine(object):

    def __init__(self, bot):
        self.bot = bot

    def primary(self, content: str, emote: str = str(), **kwargs):
        return OneLinePrimary(self.bot, emote, content, **kwargs)

    def discord(self, content: str, emote: str = str(), **kwargs):
        discord_color = self.bot.configs.color_scheme.discord
        return OneLinePrimary(self.bot, emote, content, color=discord_color, **kwargs)
