import asyncio
import discord

from .paginators import BasePaginator, FieldPaginator


class BaseMenuEntry(object):

    async def __default_parser(self, *_, **__):
        return str(self.raw)

    def __init__(self, ctx, raw, emote, page, entry_parser=None):
        self.ctx = ctx
        self.raw = raw
        self.emote = emote
        self.page = page
        self.string_parser = entry_parser or self.__default_parser
        self.string = str()

    async def get_string(self):
        self.string = await self.string_parser(self.ctx, self.raw)
        return self.string


class FieldMenuEntry(object):

    async def __default_parser(self, *_, **__):
        return str(self.raw_key), str(self.raw_value)

    def __init__(self, ctx, key, value, emote, page, parser=None):
        self.ctx = ctx
        self.raw_key = key
        self.key = str()
        self.raw_value = value
        self.value = str()
        self.emote = emote
        self.page = page
        self.parser = parser

    async def get_key_value(self):
        self.key, self.value = await self.parser(self.ctx, self.raw_key, self.raw_value)
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
            entry = self.EntryClass(self.ctx, raw_entry, self.bullets[counter], page, self.entry_parser)
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
                    raise asyncio.TimeoutError

            response = discord.utils.get(self.entries, emote=r.emoji, page=self.current_page)

            if response:
                await self._clean("Menu disabled.", self.ctx.bot.theme.images.check)
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
            entry = self.EntryClass(self.ctx, key, value, self.bullets[counter], page, self.entry_parser)
            self.entries.append(entry)
            counter += 1
            if counter == self.per_page:
                counter = 0
                page += 1


class ConfirmMenu(object):

    TRUE_STRINGS = ["yes", "yep", "yeah", "yea", ]
    FALSE_STRINGS = ["no", "nope", "negative", ]

    def __init__(self, ctx, message=None):
        self.ctx = ctx
        self.message = message or self.ctx.message
        self.emotes = [
            self.ctx.bot.emotes.misc.check,
            self.ctx.bot.emotes.misc.close
        ]
        self.confirmed = False

    def __bool__(self):
        return self.confirmed

    def __reaction_check(self, reaction, user):
        if user is None or user.id != self.ctx.author.id:
            return False
        if reaction.message.id != self.message.id:
            return False
        if reaction.emoji in self.emotes:
            return True
        return False

    def __message_check(self, message):
        if message.author.id != self.ctx.author.id:
            return False
        if message.channel.id != self.ctx.channel.id:
            return False
        if message.content in self.TRUE_STRINGS + self.FALSE_STRINGS:
            return True
        return False

    async def __clean(self):
        for emote in self.emotes:
            await self.message.remove_reaction(emote, self.ctx.me)
            await self.message.add_reaction(self.ctx.bot.emotes.misc.timer)

    async def wait_for_confirmation(self):
        if isinstance(self.message, str):
            self.message = await self.ctx.send_line(self.message, self.ctx.author.avatar_url)

        for emote in self.emotes:
            await self.message.add_reaction(emote)

        done, pending = await asyncio.wait([
            self.ctx.bot.wait_for("message", check=self.__message_check),
            self.ctx.bot.wait_for("reaction_add", check=self.__reaction_check)
        ], timeout=30, return_when=asyncio.FIRST_COMPLETED)
        try:
            response = done.pop().result()
            try:
                reaction, user = response
                if reaction.emoji == self.ctx.bot.emotes.misc.check:
                    self.confirmed = True
            except TypeError:    # discord.Message
                if response.content in self.TRUE_STRINGS:
                    self.confirmed = True
            finally:
                for emote in self.emotes:
                    await self.message.remove_reaction(emote, self.ctx.author)
                if self.confirmed:
                    await self.message.remove_reaction(self.ctx.bot.emotes.misc.close, self.ctx.me)
                else:
                    await self.message.remove_reaction(self.ctx.bot.emotes.misc.check, self.ctx.me)

        except asyncio.TimeoutError:
            await self.__clean()
        except KeyError:
            await self.__clean()

        for future in pending:
            future.cancel()
