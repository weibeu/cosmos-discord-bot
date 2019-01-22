import asyncio

from discord.ext import commands

from .functions import Loading


class CosmosContext(commands.Context):

    @property
    def emotes(self):
        return self.bot.emotes

    async def trigger_loading(self):
        async with Loading(self):
            await asyncio.sleep(10)

    async def loading(self):
        return Loading(self)
