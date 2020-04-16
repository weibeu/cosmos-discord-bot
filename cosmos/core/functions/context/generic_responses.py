from discord import Embed


class GenericResponse(Embed):

    @classmethod
    def generic(cls, emote, content):
        return cls(description=f"{emote}    {content}")
