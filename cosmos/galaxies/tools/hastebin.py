"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
        async with ctx.loading():
            url = await self.bot.utilities.haste(content)
        await ctx.send_line(f"🔗    {url}")
