from discord import Embed

from abc import abstractmethod


class Base(Embed):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Primary(Base):

    def __init__(self, bot=None, **kwargs):
        if bot:
            self.bot = bot
        primary_color = self.bot.configs.color_scheme.primary
        try:
            kwargs["color"] = kwargs.get("color") or primary_color
            kwargs.pop("colour")
        except KeyError:
            pass
        super().__init__(**kwargs)

    @property
    @abstractmethod
    def bot(self):
        if not self._bot:
            raise NotImplementedError
        return self._bot

    @bot.setter
    def bot(self, bot):
        self._bot = bot


class OneLine(Primary):

    def __init__(self, bot, content: str = None, emote: str = str(), color=None, **kwargs):
        self._bot = bot
        if emote:
            content = f"{emote}    {content}"
        assert len(content) <= 256, "Content should be less than or equal to 256 in length."
        super().__init__(title=content, color=color, **kwargs)

    @property
    def bot(self):
        return self._bot


class CosmosEmbed(object):

    def __init__(self, bot):
        self.bot = bot
        self.primary_color = self.bot.configs.color_scheme.primary

    def primary(self, **kwargs):
        return Primary(self.bot, **kwargs)

    def one_line(self, content: str, emote: str = str(), **kwargs):
        return OneLine(self.bot, emote, content, **kwargs)
