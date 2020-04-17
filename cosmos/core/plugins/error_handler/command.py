from ...functions.context.functions.paginators import NoEntriesError

import sys
import discord
import traceback

from ...functions import Cog
from cosmos import exceptions
from discord.ext import commands
from sentry_sdk import configure_scope


class CommandErrorHandler(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @staticmethod
    async def __send_response(ctx, emote_url, content):
        return await ctx.send_line(content, emote_url, color=discord.Color(0xFF1744))

    @Cog.listener()
    async def on_command_error(self, ctx, error):

        images = self.bot.theme.images

        if isinstance(error, exceptions.GuildNotPrime):
            # Tried to use prime function in non-prime guild.
            embed = ctx.embeds.primary()
            embed.set_author(name=f"🔒    Click here to get prime and unlock all features including this."
                                  f"", url="https://www.patreon.com/__thecosmos")
            await ctx.send(embed=embed)

        elif isinstance(error, exceptions.DisabledFunctionError):
            await self.__send_response(ctx, images.unavailable, "That function has been disabled in this channel.")

        elif isinstance(error, commands.BotMissingPermissions):
            await self.__send_response(
                ctx, images.mandenied,
                f"Bot is missing {error.missing_perms[0].replace('_', ' ').title()} permissions to run that command.")

        elif isinstance(error, commands.MissingPermissions):
            await self.__send_response(
                ctx, images.denied,
                f"You're missing {error.missing_perms[0].replace('_', ' ').title()} permissions to run that command.")

        elif isinstance(error, commands.CheckFailure):
            await self.__send_response(ctx, images.denied, "You're not allowed to use that command.")

        elif isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
            await self.__send_response(ctx, images.error, "Wrong command syntax. Check docs for correct usage.")

        elif isinstance(error, NoEntriesError):
            await ctx.message.add_reaction(self.bot.emotes.misc.nill)

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction(self.bot.emotes.misc.clock)

        elif isinstance(error, commands.CommandNotFound):
            pass

        else:
            with configure_scope() as scope:
                scope.user = {
                    "username": str(ctx.author), "id": ctx.author.id, "guild": ctx.guild.name, "guild_id": ctx.guild.id,
                }
            self.bot.eh.sentry.capture_exception(error)
            self.bot.log.error(f"Ignoring exception in command {ctx.command}")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
