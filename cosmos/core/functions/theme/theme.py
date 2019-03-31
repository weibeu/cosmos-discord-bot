from .models.embeds import CosmosEmbed
from .models.images import CosmosImages


class CosmosTheme(object):

    def __init__(self, bot):
        self.embeds = CosmosEmbed(bot)
        self.images = CosmosImages(bot)
