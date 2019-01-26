from .models.embeds import CosmosEmbed


class CosmosTheme(object):

    def __init__(self, bot):
        self.bot = bot
        self.embeds = CosmosEmbed(self.bot)
