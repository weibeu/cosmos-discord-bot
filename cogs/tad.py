import discord
from discord.ext import commands

class TAD(object):
    """A custom class for tad server."""

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):

        if message.author.id == 280883146872979456 and message.attachments != []:
            await message.delete()
            await message.channel.send("lol steve fuck off")

def setup(bot):
    bot.add_cog(TAD(bot))
