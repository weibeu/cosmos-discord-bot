import arrow
import discord
import random
import typing
from .. import Cog


class DeadMemes(Cog):
    """Contains worst dead shittiest dankest memes commands. Yo wait you can disable it LMAO."""

    INESCAPABLE = False

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
        message = message if isinstance(message, discord.Message) else ctx.message
        at = arrow.get(message.created_at)
        embed.set_author(name=f"{message.author} {at.humanize()} ...", icon_url=message.author.avatar_url)
        embed.description = self.mock(message.content)
        embed.set_footer(text=f"#{message.channel} | {ctx.guild.name}", icon_url=ctx.guild.icon_url)
        embed.timestamp = message.created_at
        await ctx.send(embed=embed)
