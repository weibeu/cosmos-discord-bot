from .primary import Primary


class OneLinePrimary(Primary):

    def __init__(self, bot, content: str, **kwargs):
        self._bot = bot
        assert len(content) <= 256, "Content should be less than or equal to 256 in length."
        icon_url = kwargs.get("icon_url")
        if icon_url:
            super().__init__(**kwargs)
            self.set_author(name=content, icon_url=icon_url)
        else:
            super().__init__(title=content, **kwargs)

    @property
    def bot(self):
        return self._bot


class OneLine(object):

    def __init__(self, bot):
        self.bot = bot

    def primary(self, content: str, icon_url=None, **kwargs):
        return OneLinePrimary(self.bot, content, icon_url=icon_url, **kwargs)

    def discord(self, content: str, icon_url=None, **kwargs):
        discord_color = self.bot.configs.color_scheme.discord
        return OneLinePrimary(self.bot, content, icon_url=icon_url, color=discord_color, **kwargs)
