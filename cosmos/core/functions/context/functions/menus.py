from .paginators import BasePaginator


class MenuEntry(object):

    async def __default_parser(self, *_, **__):
        return str(self.raw)

    def __init__(self, raw, emote, entry_parser=None):
        self.raw = raw
        self.emote = emote
        self.string_parser = entry_parser or self.__default_parser
        self.string = str()

    async def get_string(self):
        return await self.string_parser(self.raw)


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
        for raw_entry in self.raw_entries:
            entry = MenuEntry(raw_entry, self.bullets[counter], self.entry_parser)
            self.entries.append(entry)
            counter += 1
            if counter == self.per_page:
                counter = 0
