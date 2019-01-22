from discord.ext import commands


class CosmosContext(commands.Context):

    @property
    def emotes(self):
        return self.bot.emotes
