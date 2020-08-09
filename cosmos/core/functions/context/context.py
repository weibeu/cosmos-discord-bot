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

from .generic_responses import GenericResponse

from .functions import *

from discord.ext import commands


class CosmosContext(commands.Context):

    async def fetch_cosmos_user_profile(self, _id=None):
        return await self.bot.profile_cache.get_profile(_id or self.author.id)

    async def fetch_guild_profile(self, guild_id=None):
        try:
            return await self.bot.guild_cache.get_profile(guild_id or self.guild.id)
        except AttributeError:
            return

    async def fetch_member_profile(self, _id=None, guild_id=None):
        return await self.bot.profile_cache.get_guild_profile(_id or self.author.id, guild_id or self.guild.id)

    async def send(self, *args, **kwargs):
        if kwargs.get("embed"):
            if guild_profile := await self.fetch_guild_profile():
                if guild_profile.theme.color:
                    kwargs["embed"].color = guild_profile.theme.color
        return await super().send(*args, **kwargs)

    @property
    def responses(self):
        return GenericResponse

    async def send_response(self, emote, content):
        return await self.send(embed=self.responses.generic(emote, content))

    @property
    def emotes(self):
        return self.bot.emotes

    @property
    def embeds(self):
        return self.bot.theme.embeds

    @property
    def embed_line(self):
        return self.bot.theme.embeds.one_line.primary

    async def send_line(self, *args, delete_after=None, content=None, **kwargs):
        return await self.send(
            embed=self.bot.theme.embeds.one_line.primary(*args, **kwargs),
            delete_after=delete_after, content=content)

    async def trigger_loading(self, timeout=10):
        async with Loading(self):
            await asyncio.sleep(timeout)

    def loading(self):
        return Loading(self)

    def get_paginator(self, *args, **kwargs):
        return BasePaginator(self, *args, **kwargs)

    def get_field_paginator(self, *args, **kwargs):
        return FieldPaginator(self, *args, **kwargs)

    def get_menu(self, *args, **kwargs):
        return BaseMenu(self, *args, **kwargs)

    def get_field_menu(self, *args, **kwargs):
        return FieldMenu(self, *args, **kwargs)

    async def confirm(self, message=None, delete=False):
        menu = ConfirmMenu(self, message, delete=delete)
        await menu.wait_for_confirmation()
        return menu.confirmed
