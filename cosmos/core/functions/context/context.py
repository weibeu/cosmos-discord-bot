import asyncio

from discord.ext import commands

from .functions import Loading
from .paginators import BasePaginator


class CosmosContext(commands.Context):

    @property
    def emotes(self):
        return self.bot.emotes

    @property
    def embeds(self):
        return self.bot.theme.embeds

    @property
    def embed_line(self):
        return self.bot.theme.embeds.one_line.primary

    async def send_line(self, *args, **kwargs):
        return await self.send(embed=self.bot.theme.embeds.one_line.primary(*args, **kwargs))

    async def trigger_loading(self, timeout=10):
        async with Loading(self):
            await asyncio.sleep(timeout)

    def loading(self):
        return Loading(self)

    def get_paginator(self, entries, **kwargs):
        return BasePaginator(self, entries, **kwargs)
