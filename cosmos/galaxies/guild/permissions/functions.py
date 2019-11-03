import typing
import discord

from discord.ext import commands
from ..settings.base import Settings


class CommandConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (command := ctx.bot.get_command(argument)):
            raise commands.BadArgument
        return command


class PluginConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (plugin := ctx.bot.get_cog(argument)):
            raise commands.BadArgument
        return plugin


class GalaxyConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (galaxy := ctx.bot.get_galaxy(argument.upper())):
            raise commands.BadArgument
        return galaxy


class FunctionsPermissions(Settings):

    # TODO: Implement menu.
    # TODO: Actually implement checks for these permissions.

    @Settings.group(name="disable")
    async def disable(self, ctx, function: typing.Union[CommandConverter, PluginConverter, GalaxyConverter],
                      *channels: discord.TextChannel):
        channels = channels or ctx.channel,
        await ctx.guild_profile.permissions.disable(function, channels)
        # noinspection PyUnresolvedReferences
        await ctx.send_line(f"✅    {function.name} has been disabled in specified channels.")

    @Settings.group(name="enable")
    async def enable(self, ctx, function: typing.Union[CommandConverter, PluginConverter, GalaxyConverter],
                     *channels: discord.TextChannel):
        channels = channels or ctx.channel,
        await ctx.guild_profile.permissions.enable(function, channels)
        # noinspection PyUnresolvedReferences
        await ctx.send_line(f"✅    {function.name} has been enabled back in specified channels.")

    async def cog_command_error(self, ctx, error):
        if isinstance(error.original, AttributeError):
            await ctx.send_line(f"❌    You cannot disable that function.")
