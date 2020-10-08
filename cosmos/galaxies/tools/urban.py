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

    @staticmethod
    async def __entry_parser(_ctx, word, _words):
        return word.definition

    @Cog.cooldown(1, 3, type=Cog.bucket_type.user)
    @Cog.group("urban", aliases=["dictionary", "ud"], invoke_without_command=True)
    async def urban_dictionary(self, ctx, *, word):
        """Displays meaning and example usage of the specified word."""
        try:
            words = sorted(await self.urban.search(
                word, limit=5
            ), key=lambda w: w.votes["up"] / (w.votes["down"] or w.votes["up"] or 1), reverse=True)
        except asyncurban.WordNotFoundError:
            words = []
        if not words:
            return await ctx.send_line(f"❌    No definitions found of the specified word.")
        paginator = ctx.get_paginator(entries=words, per_page=1, entry_parser=self.__entry_parser)
        paginator.embed.set_author(
            name=f"{word.title()} | Urban Dictionary",
            icon_url="https://i.imgur.com/ysoHI9n.png", url=words[0].permalink
        )
        # paginator.embed.description = word.definition
        if words[0].example:
            paginator.embed.add_field(name=f"{self.bot.emotes.misc.test_tube}    Example", value=words[0].example)
        paginator.embed.set_footer(
            text=f"{words[0].votes['up']} Up Votes | {words[0].votes['down']} Down Votes",
            icon_url=self.bot.theme.images.rating,
        )
        await paginator.paginate()
