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
            pass    # TODO: Find all on_message's and return if bot if they using get_profile method. Don't flood here.

        elif isinstance(_value, exceptions.GuildNotFoundError):
            # Remove the guild from the internal cache. Including the GuildMemberProfile.
            if _value.guild_id:
                if _value.member_id:
                    if profile := self.bot.profile_cache.lfu.get(_value.member_id):
                        profile.guild_profiles.pop(_value.guild_id, None)
                self.bot.guild_cache.lru.pop(_value.guild_id, None)

        else:
            self.bot.eh.sentry.capture_exception(_value)
            self.bot.log.debug(f"Ignoring exception in {event}.")
            traceback.print_exception(type(_value), _value, _value.__traceback__, file=sys.stderr)
