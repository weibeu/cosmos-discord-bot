from .primary import Primary


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
