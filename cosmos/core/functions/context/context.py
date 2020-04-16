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

    async def send_line(self, *args, delete_after=None, **kwargs):
        return await self.send(embed=self.bot.theme.embeds.one_line.primary(*args, **kwargs), delete_after=delete_after)

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

    async def confirm(self, message=None):
        menu = ConfirmMenu(self, message)
        await menu.wait_for_confirmation()
        return menu.confirmed
