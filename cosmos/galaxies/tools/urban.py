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

import asyncurban

from .. import Cog


class UrbanDictionary(Cog):
    """Urban Dictionary plugin for words search."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.urban = asyncurban.UrbanDictionary()

    @Cog.cooldown(1, 3, type=Cog.bucket_type.user)
    @Cog.group("urban", aliases=["dictionary", "ud"], invoke_without_command=True)
    async def urban_dictionary(self, ctx, *, word):
        """Displays meaning and example usage of the specified word."""
        try:
            word = sorted(await self.urban.search(
                word
            ), key=lambda w: w.votes["up"] / w.votes["down"], reverse=True)[0]
        except IndexError:
            return await ctx.send_line(f"❌    No definitions found of the specified word.")
        embed = self.bot.theme.embeds.primary()
        embed.set_author(
            name=f"{word.word} | Urban Dictionary",
            icon_url="https://i.imgur.com/ysoHI9n.png", url=word.permalink
        )
        embed.description = word.definition
        if word.example:
            embed.add_field(name=f"{self.bot.emotes.misc.test_tube}    Example", value=word.example)
        embed.set_footer(
            text=f"{word.votes['up']} Up Votes | {word.votes['down']} Down Votes",
            icon_url=self.bot.theme.images.rating,
        )
        await ctx.send(embed=embed)
