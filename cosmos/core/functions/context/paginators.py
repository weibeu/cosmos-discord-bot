import asyncio

import discord


class BasePaginator(object):

    def __init__(self, ctx, entries, per_page=10, show_entry_count=False, inline=False, timeout=90, show_author=True):
        self.ctx = ctx
        self.entries = entries
        self.per_page = per_page
        self.max_pages = self.__count_pages()
        self.embed = self.ctx.bot.theme.embeds.primary
        self.is_paginating = len(self.entries) > self.per_page
        self.show_entry_count = show_entry_count
        self.inline = inline
        self.timeout = timeout
        self.show_author = show_author
        self.emotes = [
            (self.ctx.emotes.misc.backward, self.first_page),
            (self.ctx.emotes.misc.prev, self.previous_page),
            (self.ctx.emotes.misc.close, self.close),
            (self.ctx.emotes.misc.next, self.next_page),
            (self.ctx.emotes.misc.forward, self.last_page),
        ]
        self.current_page = 1
        self.message = None
        self.match = None

    def __count_pages(self):
        pages, left = divmod(len(self.entries), self.per_page)
        if left:
            pages += 1
        return pages

    def get_page(self, page):
        base = (page - 1) * self.per_page
        return self.entries[base:base + self.per_page]

    async def show_page(self, page, first=False):
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
        for reaction, _ in self.emotes:
            if self.max_pages == 2 and reaction in [self.ctx.emotes.misc.backward, self.ctx.emotes.misc.forward]:
                continue
            await self.message.add_reaction(reaction)

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
        await self.message.delete()
        self.is_paginating = False

    def check_reaction(self, reaction, user):
        if user is None or user.id != self.ctx.author.id:
            return False
        if reaction.message.id != self.message.id:
            return False

        for emote, function in self.emotes:
            if reaction.emoji == emote:
                self.match = function
                return True
        return False

    async def paginate(self):
        first_page = self.show_page(1, first=True)
        if not self.is_paginating:
            await first_page
        else:
            self.ctx.bot.loop.create_task(first_page)

        while self.is_paginating:
            try:
                _, __ = await self.ctx.bot.wait_for("reaction_add", check=self.check_reaction, timeout=self.timeout)
            except asyncio.TimeoutError:
                self.is_paginating = False
                try:
                    await self.message.clear_reaction()
                except discord.Forbidden:
                    pass
                finally:
                    break

            await self.match()
