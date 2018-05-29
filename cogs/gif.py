from discord.ext import commands
from cogs.utils import util
import discord

class Gif(object):
    """Sends cool gifs from GIPHY"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gif(self, ctx, *, query=None):
        """Sends random gif from giphy if no query is provided.
        Sends trending gif from giphy if query is `-trending`, `-trend` or `-t`.
        Otherwise searchs gets and sends gif by provided query. [Powered by GIPHY]"""
        embed = discord.Embed()
        if query is None:
            embed.set_image(url=util.get_random_gif())
            embed.color = int("0x"+util.get_random_color(), 16)
            embed.set_footer(text="Powered by GIPHY | Random Gif", icon_url="https://i.imgur.com/x2jgxuS.gif")
            async with ctx.typing():
                await ctx.send(embed=embed)
        elif query.lower() in ["-trending", "-trend", "-t"]:
            embed.set_image(url=util.get_trending_gif())
            embed.color = int("0x"+util.get_random_color(), 16)
            embed.set_footer(text="Powered by GIPHY | Trending Gif", icon_url="https://i.imgur.com/x2jgxuS.gif")
            async with ctx.typing():
                await ctx.send(embed=embed)
        else:
            embed.set_image(url=util.get_gif(query))
            embed.color = int("0x"+util.get_random_color(), 16)
            embed.set_footer(text="Powered by GIPHY | {0}".format(query), icon_url="https://i.imgur.com/x2jgxuS.gif")
            async with ctx.typing():
                await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Gif(bot))
