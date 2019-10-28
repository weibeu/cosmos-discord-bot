from discord.ext import commands

from ..settings.base import Settings


class CommandConverter(commands.Converter):

    async def convert(self, ctx, argument):
        raise commands.BadArgument


class PluginConverter(commands.Converter):

    async def convert(self, ctx, argument):
        raise commands.BadArgument


class GalaxyConverter(commands.Converter):

    async def convert(self, ctx, argument):
        raise commands.BadArgument


class FunctionsPermissions(Settings):

    async def cog_check(self, ctx):
        pass

    @Settings.group(name="disable")
    async def disable(self, ctx):
        pass

    @disable.command(name="command", aliases=["cmd"])
    async def disable_command(self, ctx, command: CommandConverter):
        pass

    @disable.command(name="plugin", aliases=["cog"])
    async def disable_plugin(self, ctx, plugin: PluginConverter):
        pass

    @disable.command(name="galaxy", aliases=["module"])
    async def disable_galaxy(self, ctx, galaxy: GalaxyConverter):
        pass

    @Settings.group(name="enable")
    async def enable(self, ctx):
        pass

    @enable.command(name="command", aliases=["cmd"])
    async def enable_command(self, ctx, command: CommandConverter):
        pass

    @enable.command(name="plugin", aliases=["cog"])
    async def enable_plugin(self, ctx, plugin: PluginConverter):
        pass

    @enable.command(name="galaxy", aliases=["module"])
    async def enable_galaxy(self, ctx, galaxy: GalaxyConverter):
        pass
