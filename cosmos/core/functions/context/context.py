import asyncio

from discord.ext import commands

from .functions import Loading


class CosmosContext(commands.Context):

    @property
    def emotes(self):
        return self.bot.emotes

    @property
    def theme(self):
        return self.bot.theme

    async def trigger_loading(self, timeout=10):
        async with Loading(self):
            await asyncio.sleep(timeout)

    def loading(self):
        return Loading(self)
