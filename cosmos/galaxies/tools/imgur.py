from discord.ext import commands

from .. import Cog
from ...core.utilities import api


class Imgur(Cog):
    """Another utility plugin which provides few commands to directly interact with imgur API."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.command(name="imgur", aliases=["imgurfy", "imgurify"])
    async def imgur(self, ctx, url=None):
        """Uploads provided URL or attached image to imgur.com and returns the direct URL of the image."""
        if not (url or ctx.message.attachments):
            raise commands.BadArgument
        url = url or ctx.message.attachments[0].url
        try:
            image = await self.bot.utilities.imgur.upload(image=url)
        except api.ImgurHTTPException:
            return await ctx.send_line("❌    Failed to upload provided image or URL to imgur.")
        return await ctx.send_line(
            "Click here to open the image in your browser.", content=f"<{image.url}>",
            icon_url=self.bot.theme.images.share, author_url=image.url)
