import discord
import datetime

from discord.ext import commands


class DevCommands(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def ss_msg(self, ctx, message_id, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        message = await channel.get_message(message_id)
        if (message.created_at - datetime.datetime.now()).days <= 6:
            time_stamp = message.created_at.strftime("%A at %I:%M %p")
        else:
            time_stamp = message.created_at.strftime("%m/%d/%Y")
        payload = {
            "name": message.author.nick or message.author.name,
            "message_content": message.clean_content,
            "avatar_url": message.author.avatar_url,
            "name_color": list(message.author.color.to_rgb()),
            "time_stamp": time_stamp
        }
        async with self.bot.session.post("http://127.0.0.1:5000/discord/ss/message/", json=payload) as response:
            screenshot = await response.read()
        
        file = discord.File(screenshot, filename="Screenshot.png")
        await ctx.send(file=file)
        


def setup(bot):
    bot.add_cog(DevCommands(bot))
