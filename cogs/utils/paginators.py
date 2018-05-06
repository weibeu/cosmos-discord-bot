import discord
from discord.ext import commands

import asyncio
import inspect


class SimplePaginator:
    """simple paginator for music palyer and help """

    def __init__(self, bot, ctx, title: str, colour, length: int=10, entries: list or tuple=None, pairs: dict=None,
                 prepend='', append='', desc: str=None, footer: str='\uFEFF', inner: str=''):
        self.bot = bot
        self.ctx = ctx
        self.title = title
        self.colour = colour
        self.length = length
        self.entries = entries
        if pairs:
            self.pairs = tuple(pairs.items())
            self.desc = desc
        else:
            self.pairs = None
            self.desc = None
        self.prepend = prepend
        self.append = append
        self.footer = footer
        self.inner = inner

        self.formatted = []
        self.pages = []

        self.current = 0
        self.controls = {'⏮': 'reset',
                         '◀': -1,
                         '⏹': 'stop',
                         '▶': +1,
                         '⏭': 'end'}
        self.controller = None

    @staticmethod
    def pager(entries, chunk: int):
        for x in range(0, len(entries), chunk):
            yield entries[x:x + chunk]

    async def stop_controller(self, message):

        try:
            await message.delete()
        except discord.HTTPException:
            pass

        del self.pages
        del self.formatted

        try:
            return self.controller.cancel()
        except Exception:
            pass

    async def react_controller(self, length: int, message, author):

        def check(r, u):

            if str(r) not in self.controls.keys():
                return False

            if u.id == self.bot.user.id or r.message.id != message.id:
                return False

            if u.id != author.id:
                return False

            return True

        while True:

            try:
                react, user = await self.bot.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                return await self.stop_controller(message)

            control = self.controls.get(str(react))

            try:
                await message.remove_reaction(react, user)
            except discord.HTTPException:
                pass

            if control == 'reset':
                self.current = 0
            elif control == 'end':
                self.current = length - 1
            elif control == 'stop':
                return await self.stop_controller(message)
            elif control == -1:
                if self.current <= 0:
                    continue
                else:
                    self.current += control
            elif control == +1:
                if self.current >= length - 1:
                    continue
                else:
                    self.current += control

            try:
                await message.edit(embed=self.pages[self.current])
            except KeyError:
                pass

    async def embed_creator(self):

        entries = self.entries or self.pairs

        chunks = list(self.pager(entries, self.length))
        count = 0
        ine_count = 0

        if self.inner:
            splat = self.inner.split('+')

        if self.entries:
            for c in chunks:
                count += 1
                embed = discord.Embed(title=f'{self.title} - Page {count}/{len(chunks)}', colour=self.colour)
                for entry in c:
                    ine_count += 1
                    if self.inner:
                        self.inner = f'{splat[0]}{ine_count}{splat[1]}'
                    self.formatted.append('{0}{1}{2}{3}'.format(self.inner, self.prepend, entry, self.append))
                entries = '\n'.join(self.formatted)
                embed.description = entries
                embed.set_footer(text=self.footer)
                self.pages.append(embed)
                del self.formatted[:]
        else:
            for c in chunks:
                count += 1
                embed = discord.Embed(title=f'{self.title} - Page {count}/{len(chunks)}', colour=self.colour)
                for entry in c:
                    embed.add_field(name=entry[0], value='{0}{1}{2}'.format(self.prepend, entry[1], self.append),
                                    inline=False)
                    embed.set_footer(text=self.footer)
                self.pages.append(embed)

        message = await self.ctx.send(embed=self.pages[0])

        if len(self.pages) <= 1:
            await message.add_reaction('⏹')
        else:
            for r in self.controls:
                try:
                    await message.add_reaction(r)
                except discord.HTTPException:
                    return

        self.controller = self.bot.loop.create_task(self.react_controller(length=len(self.pages),
                                                                          message=message,
                                                                          author=self.ctx.author))


class HelpPaginator:
    """This is bad but I just want something done for now. Will fix up later."""

    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        self.colours = {'Music': 0xD4AED9, 'Moderation': 0xF2B5C4, 'Colour': 0xdeadbf,
                        'Admin': 0xffffff, 'Eval': 0xffffff, 'KothHandler': 0xffffff, 'Plots': 0xF2B5C4,
                        'Observations': 0x8D739E, 'Dofus': 0x4DCDFF, 'Stats': 0x98FB98, 'Random': 0xFFEEC7,
                        'SubFeeds': 0x6441a5, 'Source': 0x4078c0}
        self.images = {'Dofus': 'https://i.imgur.com/4D5t5Cq.png', 'Music': 'https://i.imgur.com/DPb4hBw.png',
                       'Moderation': 'https://i.imgur.com/QJiga6E.png', 'Plots': 'https://i.imgur.com/Y8Q8siB.png',
                       'Colour': 'https://i.imgur.com/g2LpJZb.png', 'Source': 'https://i.imgur.com/DF5ZfSh.png'}
        self.ignored = ('Eval', 'Admin', 'KothHandler', 'ErrorHandler', 'BotChecks')

        self.current = 0
        self.controls = {'⏮': 'reset',
                         '◀': -1,
                         '⏹': 'stop',
                         '▶': +1,
                         '⏭': 'end'}
        self.controller = None
        self.pages = []

    async def help_generator(self):
        about = discord.Embed(title='Mysterial - Help',
                              description='For additional help and resources:\n\n'
                                          '[Support Server](http://discord.gg/Hw7RTtr)\n'
                                          '[Mysterial Web](http://mysterialbot.com/)\n'
                                          '[MystBin](http://mystbi.in)\n\n'
                                          'To use the help command, simply use the reactions below.\n'
                                          '`Only commands which {0} can use will appear.`'
                              .format(self.ctx.author.display_name)
                              , colour=0x8599ff)

        coms = sorted((cog, self.bot.get_cog_commands(cog)) for cog in self.bot.cogs if self.bot.get_cog_commands(cog))
        tcount = len([x[0] for x in coms if x[0] not in self.ignored]) + 1

        about.set_thumbnail(url=self.bot.user.avatar_url)
        self.pages.append(about)

        for x in coms:
            if x[0] in self.ignored:
                continue

            cog = self.bot.get_cog(x[0])
            embed = discord.Embed(title=x[0], description=f'```ini\n{inspect.cleandoc(cog.__doc__)}\n```',
                                  colour=self.colours[x[0]])
            image = self.images.get(x[0], 'http://pngimages.net/sites/default/files/help-png-image-34233.png')
            embed.set_thumbnail(url=image)

            ccount = 0
            for c in sorted(x[1], key=lambda n: n.name):
                ccount += 1
                short = inspect.cleandoc(c.short_doc) if c.short_doc else 'Nothing'
                if c.hidden:
                    continue
                try:
                    await c.can_run(self.ctx)
                except Exception:
                    continue

                if ccount > 9:
                    ccount = 0
                    tcount += 1

                    self.pages.append(embed)

                    embed = discord.Embed(title=x[0], description=f'```ini\n{inspect.cleandoc(cog.__doc__)}\n```',
                                          colour=self.colours[x[0]])
                    image = self.images.get(x[0], 'http://pngimages.net/sites/default/files/help-png-image-34233.png')
                    embed.set_thumbnail(url=image)

                if isinstance(c, commands.Group):
                    long = inspect.cleandoc(c.help)
                    embed.add_field(name=f'{c.name} - [Group]', value=f'{long}\n\n')
                else:
                    embed.add_field(name=c.name, value=short, inline=False)
            self.pages.append(embed)

        pcount = 1
        for em in self.pages:
            em.set_footer(text=f'Page {pcount}/{tcount}')
            pcount += 1

        message = await self.ctx.send(embed=self.pages[0])
        for r in self.controls:
            try:
                await message.add_reaction(r)
            except discord.HTTPException:
                return

        self.controller = self.bot.loop.create_task(self.react_controller(length=len(self.pages),
                                                                          message=message,
                                                                          author=self.ctx.author))

    async def stop_controller(self, message):

        try:
            await message.delete()
        except discord.HTTPException:
            pass

        try:
            return self.controller.cancel()
        except discord.HTTPException:
            return

    async def react_controller(self, length: int, message, author):

        def check(r, u):

            if str(r) not in self.controls.keys():
                return False

            if u.id == self.bot.user.id or r.message.id != message.id:
                return False

            if u.id != author.id:
                return False

            return True

        while True:

            try:
                react, user = await self.bot.wait_for('reaction_add', check=check, timeout=90)
            except asyncio.TimeoutError:
                return await self.stop_controller(message)

            control = self.controls.get(str(react))

            try:
                await message.remove_reaction(react, user)
            except discord.HTTPException:
                pass

            if control == 'reset':
                self.current = 0
            elif control == 'end':
                self.current = length - 1
            elif control == 'stop':
                return await self.stop_controller(message)
            elif control == -1:
                if self.current <= 0:
                    continue
                else:
                    self.current += control
            elif control == +1:
                if self.current >= length - 1:
                    continue
                else:
                    self.current += control

            try:
                await message.edit(embed=self.pages[self.current])
            except KeyError:
                continue
