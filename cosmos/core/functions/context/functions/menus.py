import asyncio

import discord

from .paginators import BasePaginator, FieldPaginator


class BaseMenuEntry(object):

    async def __default_parser(self, *_, **__):
        return str(self.raw)

    def __init__(self, raw, emote, page, entry_parser=None):
        self.raw = raw
        self.emote = emote
        self.page = page
        self.string_parser = entry_parser or self.__default_parser
        self.string = str()

    async def get_string(self):
        self.string = await self.string_parser(self.raw)
        return self.string


class FieldMenuEntry(object):

    async def __default_parser(self, *_, **__):
        return str(self.raw_key), str(self.raw_value)

    def __init__(self, key, value, emote, page, parser=None):
        self.raw_key = key
        self.key = str()
        self.raw_value = value
        self.value = str()
        self.emote = emote
        self.page = page
        self.parser = parser

    async def get_key_value(self):
        self.key, self.value = await self.parser(self.raw_key, self.raw_value)
        return self.key, self.value


class BaseMenu(BasePaginator):

    EntryClass = BaseMenuEntry

    def __init__(self, ctx, entries, entry_parser=None, per_page=12, *args, **kwargs):
        self.ctx = ctx
        self.raw_entries = entries
        self.entry_parser = entry_parser
        self.per_page = per_page
        self.entries = []
        self.bullets = self.ctx.bot.emotes.foods.emotes
        self.fetch_entries()
        super().__init__(self.ctx, self.entries, self.per_page, is_menu=True, *args, **kwargs)

    def fetch_entries(self):
        counter = 0
        page = 1
        for raw_entry in self.raw_entries:
            entry = self.EntryClass(raw_entry, self.bullets[counter], page, self.entry_parser)
            self.entries.append(entry)
            counter += 1
            if counter == self.per_page:
                counter = 0
                page += 1

    async def wait_for_response(self) -> EntryClass:
        first_page = self.show_page(1, first=True)
        if not self.is_paginating:
            await first_page
        else:
            self.loop.create_task(first_page)

        while self.is_paginating or self.is_menu:
            try:
                r, user = await self.ctx.bot.wait_for("reaction_add", check=self.check_reaction, timeout=self.timeout)
            except asyncio.TimeoutError:
                self.is_paginating = False
                self.is_menu = False
                try:
                    await self._clean()
                except discord.Forbidden:
                    pass
                finally:
                    break

            response = discord.utils.get(self.entries, emote=r.emoji, page=self.current_page)

            if response:
                await self._clean("Menu disabled.", self.CHECK_IMAGE_URL)
                return response
            else:
                try:
                    await self.message.remove_reaction(r, user)
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    self.ctx.bot.eh.sentry.capture_exception()

                await self.match()


class FieldMenu(BaseMenu, FieldPaginator):

    EntryClass = FieldMenuEntry

    def fetch_entries(self):
        counter = 0
        page = 1
        for key, value in self.raw_entries:
            entry = self.EntryClass(key, value, self.bullets[counter], page, self.entry_parser)
            self.entries.append(entry)
            counter += 1
            if counter == self.per_page:
                counter = 0
                page += 1
