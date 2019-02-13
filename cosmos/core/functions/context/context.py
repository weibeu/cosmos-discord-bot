import asyncio

from discord.ext import commands

from .functions import Loading
from .paginators import BasePaginator


class CosmosContext(commands.Context):

    @property
    def emotes(self):
        return self.bot.emotes

    @property
    def embed_line(self):
        return self.bot.theme.embeds.one_line.primary

    async def trigger_loading(self, timeout=10):
        async with Loading(self):
            await asyncio.sleep(timeout)

    def loading(self):
        return Loading(self)

    async def paginate(self, entries, per_page=10, show_entry_count=False, inline=False, timeout=90, show_author=True):
        return BasePaginator(self, entries, per_page, show_entry_count, inline, timeout, show_author)
