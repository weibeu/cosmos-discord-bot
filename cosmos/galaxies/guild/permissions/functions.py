import typing
import discord

from discord.ext import commands
from ..settings.base import Settings

from ....core.functions import exceptions


class CommandConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (command := ctx.bot.get_command(argument)) or argument[0].isupper():
            raise commands.BadArgument
        return command


class PluginConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (plugin := ctx.bot.get_cog(argument)):
            raise commands.BadArgument
        return plugin


class GalaxyConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (galaxy := ctx.bot.get_galaxy(argument)):
            raise commands.BadArgument
        return galaxy


class FunctionsPermissions(Settings):
    """Manage permissions of various bot functions."""

    # TODO: Implement menu.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Register following checks for permissions.
        self.bot.add_check(self.__commands_check)
        self.bot.add_check(self.__galaxies_check)

    @staticmethod
    async def __commands_check(ctx):
        try:
            if not ctx.command.inescapable:
                if ctx.channel in ctx.command.disabled_channels:
                    raise exceptions.DisabledFunctionError
            return True
        except AttributeError:
            return True

    async def __galaxies_check(self, ctx):
        try:
            plugin = ctx.command.cog.plugin
        except AttributeError:
            pass
        else:
            if ctx.command.cog.name == self.name:
                return True    # Ignore this cog.
            if plugin and not plugin.INESCAPABLE:
                if ctx.channel in plugin.disabled_channels:
                    raise exceptions.DisabledFunctionError
        return True

    @Settings.group(name="disable")
    async def disable(self, ctx, function: typing.Union[CommandConverter, PluginConverter, GalaxyConverter],
                      *channels: discord.TextChannel):
        """Disables provided function from one or multiple channels which are specified.
        A function can be any of the commands, plugins or galaxies which are allowed to be disabled.

        """
        channels = channels or (ctx.channel, )
        await ctx.guild_profile.permissions.disable(function, channels)
        # noinspection PyUnresolvedReferences
        await ctx.send_line(f"✅    {function.name} has been disabled in specified channels.")

    @Settings.group(name="enable")
    async def enable(self, ctx, function: typing.Union[CommandConverter, PluginConverter, GalaxyConverter],
                     *channels: discord.TextChannel):
        """Enables provided function in all of the specified channels.
        A function can be any of the commands, plugins or galaxies.

        """
        channels = channels or (ctx.channel, )
        await ctx.guild_profile.permissions.enable(function, channels)
        # noinspection PyUnresolvedReferences
        await ctx.send_line(f"✅    {function.name} has been enabled back in specified channels.")

    async def cog_command_error(self, ctx, error):
        if isinstance(error.original, AttributeError):
            await ctx.send_line(f"❌    You cannot disable that function.")
