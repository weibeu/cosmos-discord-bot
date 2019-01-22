from discord import NotFound


class Loading(object):

    def __init__(self, ctx):
        self.ctx = ctx
        self.emote = self.ctx.emotes.misc.yellow_square_load

    async def __do_loading(self):
        await self.ctx.message.add_reaction(self.emote)

    async def __stop_loading(self):
        try:
            await self.ctx.message.remove_reaction(self.emote, self.ctx.me)
        except NotFound:
            pass

    async def __aenter__(self):
        await self.__do_loading()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__stop_loading()
