import asyncio

import discord

from .paginators import BasePaginator


class MenuEntry(object):

    async def __default_parser(self, *_, **__):
        return str(self.raw)

    def __init__(self, ctx, raw, emote, page, entry_parser=None):
        self.raw = raw
        self.emote = emote
        self.page = page
        self.string_parser = entry_parser or self.__default_parser
        self.string = str()
        ctx.bot.loop.create_task(self.fetch_string())

    async def fetch_string(self):
        self.string = await self.string_parser(self.raw)


class BaseMenu(BasePaginator):

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
            entry = MenuEntry(self.ctx, raw_entry, self.bullets[counter], page, self.entry_parser)
            self.entries.append(entry)
            counter += 1
            if counter == self.per_page:
                counter = 0
                page += 1

    async def wait_for_response(self) -> MenuEntry:
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
