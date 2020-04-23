import sys
import traceback

from ...functions import Cog
from cosmos import exceptions


class BotErrorHandler(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.listener()
    async def on_event_error(self, event, info):
        _type, _value, _traceback = info
        if isinstance(_value, exceptions.UserIsBotError):
            pass

        else:
            self.bot.log.debug(f"Ignoring exception in {event}.")
            traceback.print_exception(type(_value), _value, _value.__traceback__, file=sys.stderr)
