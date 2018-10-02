class MyFun(object):

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if "shibu" in message.content.lower() and ("cosmos" in message.content.lower() or "cosmo" in message.content.lower()):
            await message.add_reaction('😡')
            await asyncio.sleep(7)
            await message.delete()

    async def on_member_update(self, old, new):
        if old.nick != new.nick:
            if "shibu" in new.nick.lower() and ("cosmos" in new.nick.lower() or "cosmo" in new.nick.lower()):
                await member.edit(nick="😡 | Gross")

def setup(bot):
    bot.add_cog(MyFun(bot))
