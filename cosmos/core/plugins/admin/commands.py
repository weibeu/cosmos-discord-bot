from cosmos.core.utilities.converters import CosmosUserProfileConverter, CosmosGuildConverter

import typing

from .base import Admin
from discord.ext import commands


# noinspection PyUnresolvedReferences
class AdminCommands(Admin):

    @Admin.command(name="giveprime")
    async def give_prime(self, ctx, *, target: typing.Union[CosmosUserProfileConverter, CosmosGuildConverter]):
        if not await ctx.confirm():
            return
        await target.make_prime()
        await ctx.send_line(f"🎉    {target.name} has been given prime.")

    @give_prime.error
    async def give_prime_error(self, ctx, error):
        if isinstance(error, commands.BadUnionArgument):
            return await ctx.send_line(f"❌    A dark argument was passed.")

    @Admin.command(name="removeprime")
    async def remove_prime(self, ctx, *, target: typing.Union[CosmosUserProfileConverter, CosmosGuildConverter]):
        if not await ctx.confirm():
            return
        await target.make_prime(make=False)
        await ctx.send_line(f"✅    Removed prime from {target.name}.")

    @remove_prime.error
    async def remove_prime_error(self, ctx, error):
        return await self.give_prime_error(ctx, error)

    @Admin.command(name="givefermions")
    async def give_fermions(self, ctx, user: CosmosUserProfileConverter, fermions: int):
        if not await ctx.confirm():
            return
        await user.give_fermions(fermions)
        await ctx.send_line(f"✅    Gave {fermions} fermions to {user.name}.")
