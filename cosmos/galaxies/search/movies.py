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

from discord.embeds import EmptyEmbed

from .. import Cog


class MoviesSearch(Cog):
    """Plugin for many commands related to movies."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def __display_movie(self, movie, channel):
        emotes = self.bot.emotes.misc
        embed = self.bot.theme.embeds.primary()
        embed.set_thumbnail(url=movie.poster or EmptyEmbed)
        embed.description = movie.overview
        embed.set_author(
            name=movie.title, url=movie.homepage or EmptyEmbed,
            icon_url=self.bot.theme.images.movie,
        )
        embed.set_footer(
            text=f"{movie.votes} Votes | {movie.status}",
            icon_url=self.bot.configs.tmdb.brand_icon_url
        )
        if movie.credits.director:
            embed.add_field(name=f"{emotes.director}    Director", value=movie.credits.director.name)
        if movie.credits.writer:
            embed.add_field(name=f"{emotes.draw}    Writer", value=movie.credits.writer.name)
        if movie.credits.screenplay:
            embed.add_field(name=f"{emotes.film_reel}    Screenplay", value=movie.credits.screenplay.name)
        if movie.genres:
            embed.add_field(name=f"{emotes.two_hearts}    Genres", value=", ".join(movie.genres))
        # if movie.revenue:
        #     embed.add_field(
        #         name=f"{emotes.cash}    Total Revenue",
        #         value=f"${self.bot.utilities.localize_number(movie.revenue)}"
        #     )
        if movie.release_date:
            embed.timestamp = movie.release_date
        # if movie.productions:
        #     embed.add_field(
        #         name=f"{emotes.documentary}    Productions",
        #         value=" • ".join(movie.productions), inline=False
        #     )
        if movie.credits.cast:
            embed.add_field(
                name=f"{emotes.hero}    Top Billed Cast", inline=len(embed.fields) % 2 == 0,
                value=", ".join(c.name for c in movie.credits.cast[:7])
            )
        return await channel.send(embed=embed)

    # @Cog.cooldown(1, 5, type=Cog.bucket_type.user)
    @Cog.group(name="movie", aliases=["movies"], invoke_without_command=True)
    async def movie(self, ctx, *, name):
        """Displays the details of the first movie found in search results."""
        movie = await self.bot.utilities.tmdb.fetch_movie_from_search(query=name)
        if not movie:
            return await ctx.send_line(f"❌    No movies found matching with specified name.")
        await self.__display_movie(movie, ctx.channel)
