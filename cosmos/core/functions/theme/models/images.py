class CosmosImages(dict):

    def __init__(self, bot):
        super().__init__(bot.configs.images.raw)

    def __getattribute__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError
