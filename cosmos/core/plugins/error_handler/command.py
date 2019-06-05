import sys
import traceback

from ...functions import Cog


class CommandErrorHandler(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        self.bot.eh.sentry.capture_exception(error)
        self.bot.log.error(f"Ignoring exception in command {ctx.command}")
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
