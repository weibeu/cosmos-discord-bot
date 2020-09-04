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

from discord import LoginFailure

import sys
import enum

from .tasks import InitialTasks
from .functions import CosmosContext


class Cosmos(InitialTasks):

    async def get_context(self, message, *, context_class=CosmosContext):
        return await super().get_context(message, cls=context_class)

    def run(self):
        try:
            super().run(self.configs.discord.token)
        except LoginFailure:
            self.log.error("Invalid token provided.")
            raise LoginFailure

    def get_galaxy(self, name):
        return self.plugins.get(display_name=name)

    async def on_ready(self):
        self.log.info(f"{self.user} Ready! [{self.time.round_time()} seconds.]")
        self.log.info(f"User Id: {self.user.id}")
        self.log.info("------------------------")

    async def on_error(self, event_method, *args, **kwargs):
        self.dispatch("event_error", event_method, sys.exc_info())

    async def close(self):
        profile = self.get_galaxy("PROFILE")
        try:
            await profile.cache.write_profiles(shutdown=True)
        except AttributeError:
            pass

        return await super().close()

    @enum.unique
    class PrimeTier(enum.IntEnum):

        FORMER = -1
        NONE = 0

        NEUTRINO = 1
        QUARK = 5
        STRING = 15
