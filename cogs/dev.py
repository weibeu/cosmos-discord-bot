import discord

from discord.ext import commands


class DevCommands(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ss_msg(self, ctx, message_id, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        message = await channel.get_message(message_id)
        


def setup(bot):
    bot.add_cog(DevCommands(bot))
