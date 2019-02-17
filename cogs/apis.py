import discord
from asyncurban import UrbanDictionary
from discord.ext import commands

from cogs.utils.util import get_random_embed_color


class API:

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.__get_clients())

    async def __get_clients(self):
        await self.bot.wait_until_ready()
        self.ud = UrbanDictionary(loop=self.bot.loop)

    @commands.command(name="urbandictionary", aliases=["ud", "define"])
    async def urban_dictionary(self, ctx, *, term: str):
        try:
            word = await self.ud.get_word(term)
        except asyncurban.WordNotFoundError:
            return await ctx.send(f"Unable to find `{term}` from Urban Dictionary.")
        embed = discord.Embed(title=f"{word.word} - Urban Dictionary", color=get_random_embed_color())
        embed.description = word.defination
        embed.url = word.permalink
        embed.add_field(name="Examples", value=word.example)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(API(bot))
