from .. import Cog


class HasteBin(Cog):
    """An utility plugin for Hastebin."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.cooldown(1, 4, Cog.bucket_type.guild)
    @Cog.command(name="hastebin", aliases=["haste"])
    async def haste(self, ctx, *, content):
        """Posts the provided content to https://hastebin.com/ and displays a shareable link."""
        url = await self.bot.utilities.haste(content)
        await ctx.send_line(f"🔗    {url}")
