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

    @TMDBBaseCog.cooldown(1, 5, type=TMDBBaseCog.bucket_type.user)
    @TMDBBaseCog.group(name="show", aliases=["shows", "tvshow", "tvshows"], invoke_without_command=True)
    async def tvshow(self, ctx, *, name):
        """Displays the details of the first TV Show found in the search results."""
        tvshow = await self.bot.utilities.tmdb.fetch_tvshow_from_search(query=name)
        if not tvshow:
            return await ctx.send_line(f"❌    No TV Show found matching with specified name.")
        embed = self._get_embed(tvshow, icon=self.bot.theme.images.tvshow)
        embed.set_footer(
            text=f"{embed.footer.text} | Last Air", icon_url=embed.footer.icon_url
        )
        embed.timestamp = tvshow.last_air_date
        if tvshow.creators and (tvshow.creators[0] != getattr(tvshow.credits.writer, "name", None)):
            embed.insert_field_at(0, name=f"{self.emotes.director}    Creators", value=", ".join(tvshow.creators))
        if tvshow.next_episode and tvshow.next_episode.name:
            embed.insert_field_at(
                2, name=f"{self.emotes.film_reel}    Upcoming Episode", value=tvshow.next_episode.name
            )
        else:
            if tvshow.last_episode and tvshow.last_episode.name:
                embed.insert_field_at(
                    2, name=f"{self.emotes.film_reel}    Last Episode", value=tvshow.last_episode.name
                )
        # embed.description = f"{tvshow.seasons_count} Seasons | {tvshow.episodes_count} Episodes\n" + embed.description

        await ctx.channel.send(embed=embed)
