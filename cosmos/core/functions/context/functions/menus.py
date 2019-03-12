from .paginators import BasePaginator


class MenuEntry(object):

    async def __default_parser(self, *_, **__):
        return str(self.raw)

    def __init__(self, ctx, raw, entry_parser=None):
        self.raw = raw
        self.string_parser = entry_parser or self.__default_parser
        self.string = str()
        ctx.bot.loop.create_task(self.__fetch_string())

    def __str__(self):
        return self.string

    async def __fetch_string(self):
        self.string = await self.string_parser(self.raw)


class BaseMenu(BasePaginator):

    def __init__(self, ctx, entries, entry_parser=None, *args, **kwargs):
        self.ctx = ctx
        self.raw_entries = entries
        self.entry_parser = entry_parser
        self.entries = []
        self.fetch_entries()
        super().__init__(self.ctx, self.entries, show_bullets=True, *args, **kwargs)

    def fetch_entries(self):
        for raw_entry in self.raw_entries:
            entry = MenuEntry(self.ctx, raw_entry, self.entry_parser)
            self.entries.append(entry)
