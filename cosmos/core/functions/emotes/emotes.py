from .models import GuildEmotes


class CosmosEmotes(object):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.fetch_emotes())

    async def fetch_emotes(self):
        await self.bot.wait_until_ready()
        for guild_name, guild_id in self.bot.configs.emotes.raw.items():
            guild = self.bot.get_guild(guild_id)
            emotes = GuildEmotes(guild.emojis)
            self.__setattr__(guild_name, emotes)
