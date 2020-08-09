"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
