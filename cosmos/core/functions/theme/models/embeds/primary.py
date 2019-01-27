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
