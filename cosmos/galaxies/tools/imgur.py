import typing
import discord
import mimetypes

from .. import Cog
from ...core.utilities import api


class Imgur(Cog):
    """Another utility plugin which provides few commands to directly interact with imgur API."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.cooldown(1, 5, type=Cog.bucket_type.user)
    @Cog.command(name="imgur", aliases=["imgurfy", "imgurify"])
    async def imgur(self, ctx, url: typing.Union[discord.Member, discord.Emoji, discord.PartialEmoji, str] = None):
        """Uploads provided URL or attached image to imgur.com and returns the direct URL of the image.
        You can also specify either an emoji or mention someone to upload their avatar to imgur. If no URL is
        specified, returns the imgur URL of the user's avatar.

        """
        if not (url or ctx.message.attachments):
            url = str(ctx.author.avatar_url_as(static_format="png"))

        if isinstance(url, discord.Member):
            url = str(url.avatar_url_as(static_format="png"))
        if isinstance(url, (discord.Emoji, discord.PartialEmoji)):
            url = str(url.url)
        url = url or ctx.message.attachments[0].url

        type_ = mimetypes.guess_type(url)
        if type_[0] in ("video/mp4",):
            media = dict(video=url)
        else:
            media = dict(image=url)

        try:
            async with ctx.loading():
                image = await self.bot.utilities.imgur.upload(**media)
        except api.ImgurHTTPException:
            return await ctx.send_line("❌    Failed to upload provided image or URL to imgur.")
        return await ctx.send_line(
            "Click here to open the image in your browser.", content=f"<{image.url}>",
            icon_url=self.bot.theme.images.share, author_url=image.url)
