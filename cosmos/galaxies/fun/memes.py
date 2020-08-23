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


import arrow
import random
import typing
import discord
import datetime

from .. import Cog
from discord.ext import commands


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
        file = self.bot.utilities.get_discord_file(meme_bytes, "rip.png")
        await ctx.send(file=file)

    @Cog.command(name="shotquote", aliases=["quoteshot"])
    async def shot_quote(self, ctx, from_: typing.Union[discord.Message, discord.Member], message=None):
        """This command generates and sends an image which somehow looks similar to message as it was sent by them.
        You can either specify any existing message to produce its screenshot like image or mention someone along
        with any custom text to make them say whatever you want!

        """
        if isinstance(from_, discord.Member):
            if not message:
                return await ctx.send_line("❌    Please specify any content which you want them to say.")
            author = from_
            content = message
            message = ctx.message
        else:
            author = from_.author
            content = from_.content
            message = from_
        if (datetime.datetime.now() - message.created_at).days <= 1:
            timestamp = message.created_at.strftime("Today at %I:%M %p")
        elif (datetime.datetime.now() - message.created_at).days <= 6:
            timestamp = message.created_at.strftime("%A at %I:%M %p")
        else:
            timestamp = message.created_at.strftime("%m/%d/%Y")
        screenshot_bytes = await self.bot.image_processor.discord.ss_message(
            author.display_name, content, str(author.avatar_url), author.color.to_rgb(), timestamp)
        file = self.bot.utilities.get_discord_file(screenshot_bytes, "screenshot.png")
        await ctx.send(file=file)
