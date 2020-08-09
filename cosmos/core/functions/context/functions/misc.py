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

from discord import NotFound


class Loading(object):

    def __init__(self, ctx):
        self.ctx = ctx
        self.loop = self.ctx.bot.loop
        self.emote = self.ctx.emotes.misc.square_load

    async def __do_loading(self):
        await self.ctx.message.add_reaction(self.emote)

    async def __stop_loading(self):
        try:
            await self.ctx.message.remove_reaction(self.emote, self.ctx.me)
        except NotFound:
            pass

    async def __aenter__(self):
        await self.__do_loading()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__stop_loading()

    def __enter__(self):
        self.loop.create_task(self.__aenter__())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.create_task(self.__aexit__(exc_tb, exc_val, exc_tb))

    # TODO: Replace with error reaction on_command_error.
