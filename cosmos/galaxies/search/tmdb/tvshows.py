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

from . import TMDBBaseCog


class TVShowsSearch(TMDBBaseCog):
    """Plugin for many commands related to TV Shows."""

    # @TMDBBaseCog.cooldown(1, 5, type=Cog.bucket_type.user)
    @TMDBBaseCog.group(name="show", aliases=["shows", "tvshow", "tvshows"], invoke_without_command=True)
    async def tvshow(self, ctx, *, name):
        """Displays the details of the first TV Show found in the search results."""
        tvshow = await self.bot.utilities.tmdb.fetch_tvshow_from_search(query=name)
        if not tvshow:
            return await ctx.send_line(f"❌    No TV Show found matching with specified name.")
        embed = self._get_embed(tvshow, icon=self.bot.theme.images.tvshow)
        await ctx.channel.send(embed=embed)
