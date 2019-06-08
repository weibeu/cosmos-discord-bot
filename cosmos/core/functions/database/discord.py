class DiscordDB(object):

    def __init__(self, bot):
        self.bot = bot

    @property
    def channel(self):
        return self.bot.get_channel(self.bot.configs.db.channel_id)
