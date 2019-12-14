from ...functions import Cog


class Admin(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def cog_check(self, ctx):    # ! Never ever remove this method.
        await super().cog_check(ctx)
        return await self.bot.is_owner(ctx.author)
