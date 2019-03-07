import asyncio
import discord

EmptyEmbed = discord.Embed.Empty

CANCEL_IMAGE_URL = "https://cdn.discordapp.com/attachments/553149607534919691/553154076183887872/cancel.png"


class BasePaginator(object):

    def __init__(self, ctx, entries, per_page=12, timeout=90, show_author=True, inline=False, **kwargs):
        self.ctx = ctx
        self.entries = entries
        self.per_page = per_page
        self.max_pages = self.__count_pages()
        self.embed = self.ctx.bot.theme.embeds.primary()
        self.is_paginating = len(self.entries) > self.per_page
        self.timeout = timeout
        self.show_author = show_author
        self.inline = inline
        self.show_entry_count = kwargs.get("show_entry_count", False)
        self.show_controllers = True
        self.controllers = [
            (self.ctx.emotes.misc.backward, self.first_page),
            (self.ctx.emotes.misc.prev, self.previous_page),
            (self.ctx.emotes.misc.close, self.close),
            (self.ctx.emotes.misc.next, self.next_page),
            (self.ctx.emotes.misc.forward, self.last_page),
        ]
        self.functions = []
        self.current_page = 1
        self.message = None
        self.match = None

    def __count_pages(self):
        pages, left = divmod(len(self.entries), self.per_page)
        if left:
            pages += 1
        return pages

    async def set_controllers(self, **kwargs):
        if self.show_controllers:
            for reaction, _ in self.controllers:
                if self.max_pages == 2 and reaction in [self.ctx.emotes.misc.backward, self.ctx.emotes.misc.forward]:
                    continue
                if not kwargs.get(reaction.name, True):
                    continue
                await self.message.add_reaction(reaction)
        for reaction, _ in self.functions:
            await self.message.add_reaction(reaction)

    def get_page(self, page):
        base = (page - 1) * self.per_page
        return self.entries[base:base + self.per_page]

    async def show_page(self, page, first=False, **kwargs):
        self.current_page = page
        entries = self.get_page(page)
        para = []
        for index, entry in enumerate(entries, 1 + (page - 1) * self.per_page):
            if self.show_entry_count:
                para.append(f"{index}. {entry}")
            else:
                para.append(entry)

        if self.max_pages > 1:
            if self.show_entry_count:
                text = f"Displaying {page} of {self.max_pages} pages and {len(entries)} entries."
            else:
                text = f"Displaying {page} of {self.max_pages} pages."
            self.embed.set_footer(text=text)

        if self.show_author:
            self.embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.avatar_url)

        if not self.is_paginating:
            self.embed.description = "\n".join(para)
            return await self.ctx.send(embed=self.embed)

        if not first:
            self.embed.description = "\n".join(para)
            return await self.message.edit(embed=self.embed)

        para.append(str())

        self.embed.description = "\n".join(para)
        self.message = await self.ctx.channel.send(embed=self.embed)

        await self.set_controllers(**kwargs)

    async def check_show_page(self, page):
        if page != 0 and page <= self.max_pages:
            await self.show_page(page)

    async def first_page(self):
        await self.show_page(1)

    async def last_page(self):
        await self.show_page(self.max_pages)

    async def next_page(self):
        await self.check_show_page(self.current_page + 1)

    async def previous_page(self):
        await self.check_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.is_paginating:
            await self.show_page(self.current_page)

    async def close(self):
        self.embed.set_footer(text="You closed this menu.", icon_url=CANCEL_IMAGE_URL)
        await self.message.edit(embed=self.embed)
        await self.message.clear_reactions()
        self.is_paginating = False

    def add_function(self, emote, function):
        self.functions.append((emote, function))

    def check_reaction(self, reaction, user):
        if user is None or user.id != self.ctx.author.id:
            return False
        if reaction.message.id != self.message.id:
            return False

        for emote, function in self.controllers + self.functions:
            if reaction.emoji == emote:
                self.match = function
                if (emote, function) in self.functions:
                    self.embed.set_footer(text=EmptyEmbed, icon_url=EmptyEmbed)
                return True
        return False

    async def paginate(self, show_controllers=True, **kwargs):
        self.show_controllers = show_controllers
        first_page = self.show_page(1, first=True, **kwargs)
        if not self.is_paginating:
            await first_page
        else:
            self.ctx.bot.loop.create_task(first_page)

        while self.is_paginating:
            try:
                r, user = await self.ctx.bot.wait_for("reaction_add", check=self.check_reaction, timeout=self.timeout)
            except asyncio.TimeoutError:
                self.is_paginating = False
                try:
                    self.embed.set_footer(text="This menu was closed due to inactivity.", icon_url=CANCEL_IMAGE_URL)
                    await self.message.edit(embed=self.embed)
                    await self.message.clear_reactions()
                except discord.Forbidden:
                    pass
                finally:
                    break

            try:
                await self.message.remove_reaction(r, user)
            except discord.Forbidden:
                pass
            except discord.NotFound:
                self.ctx.bot.eh.sentry.capture_exception()

            await self.match()


class FieldPaginator(BasePaginator):

    async def show_page(self, page, first=False, **kwargs):
        self.current_page = page
        entries = self.get_page(page)
        self.embed.clear_fields()

        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=self.inline)

        if self.max_pages > 1:
            if self.show_entry_count:
                text = f"Displaying {page} of {self.max_pages} pages and {len(entries)} entries."
            else:
                text = f"Displaying {page} of {self.max_pages} pages."
            self.embed.set_footer(text=text)

        if self.show_author:
            self.embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.avatar_url)

        if not self.is_paginating:
            return await self.ctx.send(embed=self.embed)

        if not first:
            return await self.message.edit(embed=self.embed)

        self.message = await self.ctx.channel.send(embed=self.embed)

        await self.set_controllers(**kwargs)
