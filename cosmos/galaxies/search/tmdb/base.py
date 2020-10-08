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

from ... import Cog


class TMDBBaseCog(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.emotes = None

    @Cog.listener()
    async def on_ready(self):
        self.emotes = self.bot.emotes.misc

    def _get_embed(self, instance, icon):
        embed = self.bot.theme.embeds.primary()
        embed.set_thumbnail(url=instance.poster or EmptyEmbed)
        embed.description = instance.overview
        embed.set_author(name=instance.title, url=instance.homepage or EmptyEmbed, icon_url=icon)
        if instance.credits.director:
            embed.add_field(name=f"{self.emotes.director}    Director", value=instance.credits.director.name)
        if instance.credits.writer:
            embed.add_field(name=f"{self.emotes.draw}    Writer", value=instance.credits.writer.name)
        if instance.credits.screenplay:
            embed.add_field(name=f"{self.emotes.film_reel}    Screenplay", value=instance.credits.screenplay.name)
        if instance.genres:
            embed.add_field(name=f"{self.emotes.two_hearts}    Genres", value=", ".join(instance.genres))
        # if instance.revenue:
        #     embed.add_field(
        #         name=f"{self.emotes.cash}    Total Revenue",
        #         value=f"${self.bot.utilities.localize_number(instance.revenue)}"
        #     )
        if instance.release_date:
            embed.timestamp = instance.release_date
        # if instance.productions:
        #     embed.add_field(
        #         name=f"{self.emotes.documentary}    Productions",
        #         value=" • ".join(instance.productions), inline=False
        #     )
        if instance.credits.cast:
            embed.add_field(
                name=f"{self.emotes.hero}    Top Billed Cast", inline=False,    # len(embed.fields) % 2 == 0,
                value=", ".join(c.name for c in instance.credits.cast[:7])
            )
        embed.set_footer(
            text=f"{instance.votes} Votes | {instance.status}",
            icon_url=self.bot.configs.tmdb.brand_icon_url
        )
        return embed
