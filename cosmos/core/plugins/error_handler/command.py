import sys
import traceback

from ...functions import Cog
from cosmos import exceptions


class CommandErrorHandler(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # Do the basic logging first.
        self.bot.eh.sentry.capture_exception(error)
        self.bot.log.error(f"Ignoring exception in command {ctx.command}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        if isinstance(error, exceptions.GuildNotPrime):
            # Tried to use prime function in non-prime guild.
            embed = ctx.embeds.primary()
            embed.set_author(name=f"🔒    Click here to get prime and unlock all features including this."
                                  f"", url="https://www.patreon.com/__thecosmos")
            await ctx.send(embed=embed)
