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

from discord.ext import commands

import io
import arrow
import discord
import random
import typing

from .. import Cog


class DeadMemes(Cog):
    """Contains worst dead shittiest dankest memes commands. Yo wait you can disable it LMAO."""

    INESCAPABLE = False

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @staticmethod
    def mock(text, diversity_bias=0.5, random_seed=None):
        if diversity_bias < 0 or diversity_bias > 1:
            raise ValueError('diversity_bias must be between the inclusive range [0,1].')
        random.seed(random_seed)
        out = ''
        last_was_upper = True
        swap_chance = 0.5
        for c in text:
            if c.isalpha():
                if random.random() < swap_chance:
                    last_was_upper = not last_was_upper
                    swap_chance = 0.5
                c = c.upper() if last_was_upper else c.lower()
                swap_chance += (1 - swap_chance) * diversity_bias
            out += c
        return out

    @Cog.command("spongebobmock")
    async def sponge_bob_mock(self, ctx, *, message: typing.Union[discord.Message, str]):
        """Spongebob mocks provided message or text and sends it back."""
        embed = ctx.embeds.primary()
        if isinstance(message, discord.Message):
            target = message
            content = message.content
            guild = message.guild
        else:
            target = ctx.message
            content = message
            guild = ctx.guild
        if not content:
            try:
                _embed = message.embeds[0]
            except IndexError:
                return
            else:
                if not (content := _embed.description):
                    return
        at = arrow.get(target.created_at)
        name = target.author.nick or target.author.name
        embed.set_author(name=f"{name} {at.humanize()} ...", icon_url=target.author.avatar_url)
        embed.description = self.mock(await commands.clean_content().convert(ctx, content))
        embed.set_footer(text=f"#{target.channel} | {guild.name}", icon_url=guild.icon_url)
        embed.timestamp = target.created_at
        await ctx.send(embed=embed)

    @Cog.command(name="rip")
    async def rip(self, ctx, member: discord.Member = None):
        """Sends the worst and shittiest rip meme."""
        member = member or ctx.author
        meme_bytes = await self.bot.image_processor.memes.rip(member.name, str(member.avatar_url))
        file = discord.File(io.BytesIO(meme_bytes), filename="rip.png")
        await ctx.send(file=file)
