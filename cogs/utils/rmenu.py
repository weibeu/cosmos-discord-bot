import asyncio
import discord
from cogs.utils import util

class Menu(object):
    """Reaction based menu."""

    def __init__(self, ctx, *, entries, per_page=7, show_entry_count=True, inline=False):
        self.ctx = ctx
        self.bot = ctx.bot
        self.entries = entries
        self.message = ctx.message
        self.author = ctx.author
        self.channel = ctx.channel
        self.per_page = per_page
        pages, left_over = divmod(len(self.entries), self.per_page)
        if left_over:
            pages += 1
        self.max_pages = pages
        self.embed = discord.Embed(colour=util.get_random_embed_color())
        self.paginating = len(entries) > per_page
        self.show_entry_count = show_entry_count
        self.nav_emojis = [
            ('\N{BLACK LEFT-POINTING TRIANGLE}', self.previous_page),
            ('\N{BLACK SQUARE FOR STOP}', self.stop_pages),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.next_page)
        ]
        self.reaction_emojis = util.get_reaction_numbers()
        self.choices = {}
        self.inline = inline

    def get_page(self, page):
        base = (page - 1) * self.per_page
        return self.entries[base:base + self.per_page]

    async def show_page(self, page, *, first=False):
        self.current_page = page
        entries = self.get_page(page)
        p = []
        remojis = []
        for index, entry in enumerate(entries, 1 + ((page - 1) * self.per_page)):
            p.append(f'{index}. {entry}')
            self.choices[self.reaction_emojis[str(index)]] = index
            remojis.append(self.reaction_emojis[str(index)])
        if self.max_pages > 1:
            if self.show_entry_count:
                text = f'Page {page}/{self.max_pages} ({len(self.entries)} entries)'
            else:
                text = f'Page {page}/{self.max_pages}'
            self.embed.colour = util.get_random_embed_color()
            self.embed.set_footer(text=text)
        if not self.paginating:
            self.embed.description = '\n'.join(p)
            self.embed.set_author(name=self.author.name, icon_url=self.author.avatar_url)
            self.message = await self.channel.send(embed=self.embed)
            for r in remojis:
                await self.message.add_reaction(r)
            await self.message.add_reaction('\N{BLACK SQUARE FOR STOP}')
            return self.message
        if not first:
            self.embed.description = '\n'.join(p)
            await self.message.edit(embed=self.embed)
            for r in remojis:
                await self.message.add_reaction(r)
            for (reaction, _) in self.nav_emojis:
                if self.max_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                    # no |<< or >>| buttons if we only have two pages
                    # we can't forbid it if someone ends up using it but remove
                    # it from the default set
                    continue

                await self.message.add_reaction(reaction)
            return
        p.append('')
        self.embed.description = '\n'.join(p)
        self.embed.set_author(name=self.author.name, icon_url=self.author.avatar_url)
        self.message = await self.channel.send(embed=self.embed)
        for r in remojis:
            await self.message.add_reaction(r)
        for (reaction, _) in self.nav_emojis:
            if self.max_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                # no |<< or >>| buttons if we only have two pages
                # we can't forbid it if someone ends up using it but remove
                # it from the default set
                continue

            await self.message.add_reaction(reaction)

    async def checked_show_page(self, page):
        if page != 0 and page <= self.max_pages:
            await self.show_page(page)

    async def next_page(self):
        """goes to the next page"""
        await self.checked_show_page(self.current_page + 1)

    async def previous_page(self):
        """goes to the previous page"""
        await self.checked_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.paginating:
            await self.show_page(self.current_page)

    async def stop_pages(self):
        """stops the interactive pagination session"""
        await self.message.delete()
        self.paginating = False

    def react_check(self, reaction, user):
        if user is None or user.id != self.author.id:
            return False

        if reaction.message.id != self.message.id:
            return False

        for (emoji, func) in self.nav_emojis:
            if reaction.emoji == emoji:
                self.match = func
                return True

        if reaction.emoji in list(self.choices.keys()) or reaction.emoji.name+":"+str(reaction.emoji.id) in list(self.choices.keys()):
            return True

        return False

    async def paginate(self):
        """Actually paginate the entries and run the interactive loop if necessary."""
        first_page = self.show_page(1, first=True)
        if not self.paginating:
            await first_page
            def check(reaction, user):
                return user == self.author
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=self.react_check, timeout=120.0)
            except asyncio.TimeoutError:
                try:
                    await self.message.clear_reactions()
                except:
                    pass
            if reaction.emoji == '\N{BLACK SQUARE FOR STOP}':
                await self.ctx.message.delete()
                await self.message.delete()
                return
            try:
                if reaction.emoji in list(self.choices.keys()) or reaction.emoji.name+":"+str(reaction.emoji.id) in list(self.choices.keys()):
                    index = self.choices[reaction.emoji.name+":"+str(reaction.emoji.id)]
                    await self.ctx.message.delete()
                    await self.message.delete()
                    return index - 1
            except AttributeError:
                await self.message.clear_reactions()

            await self.match()
        else:
            # allow us to react to reactions right away if we're paginating
            self.bot.loop.create_task(first_page)

        while self.paginating:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=self.react_check, timeout=120.0)
            except asyncio.TimeoutError:
                self.paginating = False
                try:
                    await self.message.clear_reactions()
                except:
                    pass
                finally:
                    break

            try:
                if reaction.emoji in list(self.choices.keys()) or reaction.emoji.name+":"+str(reaction.emoji.id) in list(self.choices.keys()):
                    index = self.choices[reaction.emoji.name+":"+str(reaction.emoji.id)]
                    await self.ctx.message.delete()
                    await self.message.delete()
                    return index - 1
                    break
            except AttributeError:
                if (self.current_page == 1 and reaction.emoji == '\N{BLACK LEFT-POINTING TRIANGLE}') or (self.current_page == self.max_pages and reaction.emoji == '\N{BLACK RIGHT-POINTING TRIANGLE}'):
                    await self.message.remove_reaction(reaction, user)
                else:
                    await self.message.clear_reactions()

            await self.match()

class FieldMenu(Menu):
    """Similar to Pages except entries should be a list of
    tuples having (key, value) to show as embed fields instead.
    """
    async def show_page(self, page, *, first=False):
        self.current_page = page
        entries = self.get_page(page)
        remojis = []
        self.embed.clear_fields()
        index = 1 + ((page - 1) * self.per_page)
        for key, value in entries:
            self.embed.add_field(name="<:"+self.reaction_emojis[str(index)]+"> "+str(key), value=str(value), inline=self.inline)
            self.choices[self.reaction_emojis[str(index)]] = index
            remojis.append(self.reaction_emojis[str(index)])
            index += 1

        if self.max_pages > 1:
            if self.show_entry_count:
                text = f'Page {page}/{self.max_pages} ({len(self.entries)} entries)'
            else:
                text = f'Page {page}/{self.max_pages}'

            self.embed.set_footer(text=text)
        self.embed.colour = util.get_random_embed_color()
        if not self.paginating:
            self.embed.set_author(name=self.author.name, icon_url=self.author.avatar_url)
            self.message = await self.channel.send(embed=self.embed)
            for r in remojis:
                await self.message.add_reaction(r)
            await self.message.add_reaction('\N{BLACK SQUARE FOR STOP}')
            return self.message

        if not first:
            await self.message.edit(embed=self.embed)
            for r in remojis:
                await self.message.add_reaction(r)
            for (reaction, _) in self.nav_emojis:
                if self.max_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                    # no |<< or >>| buttons if we only have two pages
                    # we can't forbid it if someone ends up using it but remove
                    # it from the default set
                    continue

                await self.message.add_reaction(reaction)
            return
        self.embed.set_author(name=self.author.name, icon_url=self.author.avatar_url)
        self.message = await self.channel.send(embed=self.embed)
        for r in remojis:
            await self.message.add_reaction(r)
        for (reaction, _) in self.nav_emojis:
            if self.max_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                # no |<< or >>| buttons if we only have two pages
                # we can't forbid it if someone ends up using it but remove
                # it from the default set
                continue

            await self.message.add_reaction(reaction)

async def confirm_menu(ctx, message, custom_message=False):

    if custom_message:
        m = message
    else:
        m = await ctx.send(message)

    def react_check(reaction, user):
        if user is None or user.id != ctx.author.id:
            return False

        if reaction.message.id != m.id:
            return False

        if reaction.emoji.name+":"+str(reaction.emoji.id) in list(util.get_reaction_yes_no().values()):
            return True

        return False

    for choice in util.get_reaction_yes_no():
        await m.add_reaction(util.get_reaction_yes_no()[choice])
    try:
        choice, user = await ctx.bot.wait_for('reaction_add', timeout=120.0, check=react_check)
    except asyncio.TimeoutError:
        await ctx.send("Reaction Timeout")
    if choice.emoji.name+":"+str(choice.emoji.id) == util.get_reaction_yes_no()["yes"]:
        await m.delete()
        return True
    elif choice.emoji.name+":"+str(choice.emoji.id) == util.get_reaction_yes_no()["no"]:
        await m.delete()
        await ctx.send("Cancelled!")
        return False
    else:
        await m.delete()
        await ctx.send("Some problem with yes/no reactions in confirm_menu.")
        return False
