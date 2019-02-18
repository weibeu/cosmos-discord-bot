import asyncio

import discord
from asyncurban import UrbanDictionary
from discord.ext import commands

from cogs.utils.paginator import Pages
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
        paginator = Pages(ctx, entries=word.definition.splitlines(), per_page=8, show_entry_count=False, show_author=False)
        paginator.embed.set_author(name=f"{word.word} - Urban Dictionary", url=word.permalink, icon_url=ctx.author.avatar_url)
        async def show_help(p):
            p.embed.description = p.Empty
            p.embed.add_field(name="Examples", value=word.example)
            await p.message.edit(embed=p.embed)
            await asyncio.sleep(60)
            await p.show_current_page()
        p.show_help = show_help
        await paginator.paginate()


def setup(bot):
    bot.add_cog(API(bot))
