import discord
import typing

from .events import LoggerEvents
from discord.ext import commands


class NameConvertor(commands.Converter):

    async def convert(self, ctx, argument):
        if not argument.lower().startswith("on"):
            raise commands.BadArgument("Logger name doesn't starts with 'on'.")
        if " " in argument:
            return argument.lower().replace(" ", "_")
        return argument


class Logger(LoggerEvents):

    @staticmethod
    async def __logger_entry_parser(_, entry, __):
        return entry.replace("_", " ").title()

    @LoggerEvents.group(name="logger", aliases=["log", "logging"])
    @commands.has_permissions(administrator=True)
    async def logger(self, ctx):
        pass

    @logger.command(name="enable", aliases=["create"])
    async def enable_logger(self, ctx, channel: typing.Optional[discord.TextChannel], *, name: NameConvertor = None):
        channel = channel or ctx.channel
        guild_profile = await ctx.fetch_guild_profile()
        loggers = [name for name in self.loggers if not guild_profile.get_logger(name)]
        if not name:
            menu = ctx.get_menu(loggers, entry_parser=self.__logger_entry_parser)
            response = await menu.wait_for_response()
            name = response.entry
        if name not in self.loggers:
            return await ctx.send_line(f"❌    Sorry but logging for event '{name}' isn't supported yet.")
        logger = guild_profile.get_logger(name)
        if logger:
            return await ctx.send_line(f"❌    Logs for event '{logger.name}' is already enabled in #{logger.channel}")

        await guild_profile.enable_logger(name, channel)
        await ctx.send_line(f"✅    Logs for event '{name}' has been enabled in #{channel.name} channel.")

    @logger.command(name="disable", aliases=["remove"])
    async def disable_logger(self, ctx, *, name=None):
        guild_profile = await ctx.fetch_guild_profile()
        loggers = [logger.name for logger in guild_profile.loggers]
        if not name:
            menu = ctx.get_menu(loggers, entry_parser=self.__logger_entry_parser)
            response = await menu.wait_for_response()
            name = response.entry
        if name not in self.loggers:
            return await ctx.send_line(f"❌    Sorry but logging for event '{name}' isn't supported yet.")
        logger = guild_profile.get_logger(name)
        if not logger:
            return await ctx.send_line(f"❌    Logs for event '{name}' isn't' enabled yet.")

        await guild_profile.remove_logger(name)
        await ctx.send_line(f"✅    Logs for event '{name}' has been removed.")
