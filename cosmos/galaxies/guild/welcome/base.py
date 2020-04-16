from ..settings.base import Settings


class WelcomeBase(Settings):

    @Settings.group(name="welcome", aliases=["join"])
    async def welcome(self, ctx):
        """Manage different welcome settings of your server."""
        pass


class MessageTemplateMember(object):

    __slots__ = ("id", "username", "name", "discriminator", "mention")

    def __init__(self, author):
        self.id = author.id
        self.username = str(author)
        self.name = author.name
        self.discriminator = author.discriminator
        self.mention = author.mention
