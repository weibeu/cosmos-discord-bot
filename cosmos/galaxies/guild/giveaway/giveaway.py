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

from ....core.functions.exceptions import GuildNotPrime
from ....core.utilities import converters
from .._models import GuildBaseCog

import typing
import re
import discord

from discord.ext.commands import MissingPermissions


_MESSAGE_TRIGGER_REGEX = re.compile(
    r"(?:.+(?:\s?))?(?:participate|host(?:ing)?|sponsor(?:ing)?)\s?(?:in|for|this)?\s?"
    r"(?:[*][*]\s?)(.+(?:\s?))(?:[*][*]\s?)giveaway(?:.+(?:\s?))?", re.IGNORECASE
)


class _FakeContext(object):

    pass


class Giveaway(GuildBaseCog):
    """Create interactive giveaways in your server.

    There are two ways you can host a giveaway in your server. You may either make use of the ;giveaway command
    or include some special syntax in your own message to make bot trigger for the giveaway over this message.

    SYNTAX: ... participate in **{reward}** giveaway ...

    """

    def __init__(self, plugin):
        super().__init__(plugin)
        self.bot.scheduler.register_callback(self.__giveaway_prize)

    async def cog_check(self, ctx):
        await super().cog_check(ctx)
        if not ctx.author.guild_permissions.manage_guild:
            raise MissingPermissions(["manage_guild"])
        return True

    async def __giveaway_prize(self, _task, *, channel_id, reward, **kwargs):
        embed = self.bot.theme.embeds.one_line.primary
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
        except discord.NotFound:
            return
        message = await channel.fetch_message(kwargs["message_id"])

        users = [
            _ for _ in await message.reactions[0].users().flatten() if
            isinstance(_, discord.Member) and not _.bot
        ]
        if not users:
            return await channel.send(embed=embed(f"☹    Did you all really missed the giveaway that easily?"))
        winners = self.bot.utilities.get_random_elements([_ for _ in users if not _.bot], kwargs["winners"])

        content = " ".join(w.mention for w in winners)

        await channel.send(content=content, embed=embed(
            f"Congratulations to the winners for winning {reward}.", self.bot.theme.images.prize
        ))

    async def get_giveaways(self, guild_id):
        return list(await self.bot.scheduler.fetch_tasks(self.__giveaway_prize, guild_id=guild_id))

    async def create_giveaway(self, reward, channel, message=None, winners=1, duration=None):
        if not duration:
            duration = await converters.HumanTimeDeltaConverter(
            ).convert(_FakeContext(), self.plugin.data.giveaway.default_life)
        if not message:
            embed = self.bot.theme.embeds.one_line.primary(reward, self.bot.theme.images.prize)
            embed.description = f"React to this message with {self.bot.emotes.misc.confetti} to participate."
            embed.set_footer(text=f"{winners} winners | Ends at")
            embed.timestamp = duration.datetime
            message = await channel.send(embed=embed)
        await message.add_reaction(self.bot.emotes.misc.confetti)
        await self.bot.scheduler.schedule(
            "__giveaway_prize", duration.datetime, winners=winners, reward=reward,
            channel_id=channel.id, message_id=message.id, guild_id=channel.guild.id
        )

    @GuildBaseCog.listener()
    async def on_message(self, message):
        try:
            reward = _MESSAGE_TRIGGER_REGEX.findall(message.content)[0]
        except IndexError:
            return
        if not message.author.guild_permissions.administrator:
            return
        await self.create_giveaway(reward, message.channel, message=message)

    @GuildBaseCog.group(name="giveaway", aliases=["giveaways", "ga"])
    async def giveaway(
            self, ctx, duration: converters.HumanTimeDeltaConverter,
            winners: typing.Optional[int] = 1, channel: typing.Optional[discord.TextChannel] = None, *, reward
    ):
        """Creates giveaway in the server and waits for members to participate by reacting to the message.

        You must always specify the duration of the giveaway to let members to participate. It can be in format
        of xseconds, xmins, xhours, xweeks ...

        By default it randomly chooses one winner from all members who had participated. To change, specify desired
        number of winners to pick randomly.

        """
        channel = channel or ctx.channel
        if duration.delta.days >= self.plugin.data.giveaway.max_life and not ctx.guild_profile.is_prime:
            raise GuildNotPrime("Get prime to host giveaways beyond age of universe and more features.")
        giveaways = await self.get_giveaways(ctx.guild.id)
        if len(giveaways) > self.plugin.data.giveaway.max_giveaways and not ctx.guild_profile.is_prime:
            raise GuildNotPrime("Get prime to create unlimited giveaways and more features.")
        # noinspection PyTypeChecker
        await self.create_giveaway(reward, channel, winners=winners, duration=duration)

    # TODO: Provide extra giveaway management command.
