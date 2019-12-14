import typing
import discord

from .base import Admin


class AdminCommands(Admin):

    @Admin.group(name="give")
    async def give_(self, ctx):
        pass

    @give_.command(name="prime")
    async def give_prime(self, ctx, *, target: typing.Union[discord.User, int]):
        if isinstance(target, int):
            target = await ctx.fetch_guild_profile()

