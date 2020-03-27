from ...functions.context.functions.paginators import NoEntriesError

import sys
import traceback

from ...functions import Cog
from cosmos import exceptions
from discord.ext import commands


class CommandErrorHandler(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, exceptions.GuildNotPrime):
            # Tried to use prime function in non-prime guild.
            embed = ctx.embeds.primary()
            embed.set_author(name=f"🔒    Click here to get prime and unlock all features including this."
                                  f"", url="https://www.patreon.com/__thecosmos")
            await ctx.send(embed=embed)

        elif isinstance(error, (commands.MissingPermissions, commands.CheckFailure)):
            await ctx.message.add_reaction(self.bot.emotes.misc.denied)

        elif isinstance(error, commands.BadArgument):
            await ctx.message.add_reaction(self.bot.emotes.misc.error)

        elif isinstance(error, NoEntriesError):
            await ctx.message.add_reaction(self.bot.emotes.misc.nill)

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction(self.bot.emotes.misc.clock)

        else:
            self.bot.eh.sentry.capture_exception(error)
            self.bot.log.error(f"Ignoring exception in command {ctx.command}")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
