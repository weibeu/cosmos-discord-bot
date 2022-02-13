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

import discord
import typing
import datetime

from discord.ext import commands

from ....core.functions.exceptions import GuildNotPrime
from ....core.utilities import converters, time
from .base import RoleShopBase, DeletedRole
from discord.ext.commands import has_permissions


class RoleShopSettings(RoleShopBase):
    """A plugin to manage and setup Role Shop in server."""

    def __init__(self, plugin):
        super().__init__(plugin)
        self.bot.scheduler.register_callback(self.__raffle_points)

    @RoleShopBase.command(name="givepoints", aliases=["givepoint"])
    @has_permissions(administrator=True)
    async def give_points(self, ctx, points: int, *, member: discord.Member):
        """Generate and give points to specified member. You can also specify negative points to remove points."""
        if member.bot:
            return await ctx.send_line("❌    You can't give points to robots.")
        profile = await ctx.fetch_member_profile(member.id)
        try:
            profile.give_points(points)
        except OverflowError:
            return await ctx.send_line("❌    They can't have such insane number of points.")
        await ctx.send_line(f"✅    Gave {points} points to {member.display_name}.")

    async def __raffle_points(self, _task, *, channel_id, points, **kwargs):
        embed = self.bot.theme.embeds.one_line.primary
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
        except discord.NotFound:
            return
        message = await channel.fetch_message(kwargs["message_id"])
        users = [
            _ for _ in await message.reactions[0].users().flatten() if
            isinstance(_, discord.Member) and not (_.bot or _.guild_permissions.manage_roles)
        ]
        if not users:
            return await channel.send(embed=embed(f"☹    Did you all really let it go that easily?"))
        winners = self.bot.utilities.get_random_elements([_ for _ in users if not _.bot], kwargs["winners"])

        content = str()
        for winner in winners:
            profile = await self.bot.profile_cache.get_guild_profile(winner.id, message.guild.id)
            profile.give_points(points)
            content += f" {winner.mention}"

        await channel.send(content=content,embed=embed(
            f"Congratulations to the winners for winning the raffle with {points} points.", self.bot.theme.images.prize
        ))

    async def get_raffles(self, guild_id):
        return list(await self.bot.scheduler.fetch_tasks(self.__raffle_points, guild_id=guild_id))

    @RoleShopBase.command(name="rafflepoints", aliases=["rafflepoint"])
    @has_permissions(administrator=True)
    async def raffle_points(
            self, ctx, points: int, winners: typing.Optional[int] = 1, *, end: converters.HumanTimeDeltaConverter = None
    ):
        """Raffles points among the members who react to the confetti reaction to specified number of winners.
        Defaults to 1 winner. By default, raffle will last till 7 seconds. If you want it to last for desired
        time then you should specify when it should end.

        """
        end = end or time.HumanDateTimeMixin.from_using_timedelta(minutes=self.plugin.data.roleshop.default_raffle_life)
        if end.delta.days >= self.plugin.data.roleshop.max_raffle_life and not ctx.guild_profile.is_prime:
            raise GuildNotPrime("Get prime to schedule raffles beyond age of universe and other features.")
        raffles = await self.get_raffles(ctx.guild.id)
        if len(raffles) > self.plugin.data.roleshop.max_raffles and not ctx.guild_profile.is_prime:
            raise GuildNotPrime("Click to get prime to created unlimited raffles and more features.")
        message = await ctx.send_line(
            f"React to participate in raffle worth {points} points.", self.bot.theme.images.confetti)
        await message.add_reaction(self.bot.emotes.misc.animated_heart)
        await self.bot.scheduler.schedule(
            "__raffle_points", end.datetime if end else datetime.datetime.utcnow() + datetime.timedelta(seconds=7),
            channel_id=ctx.channel.id, message_id=message.id, points=points, winners=winners, guild_id=ctx.guild.id)

    @RoleShopBase.role_shop.command(name="create")
    @commands.bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def create_role(self, ctx, points: int, *, role: typing.Union[discord.Role, str]):
        """Create a new or use specified role for the Role Shop."""
        if len(ctx.guild_profile.roleshop.roles) >= self.plugin.data.roleshop.max_roles:
            res = f"❌    Sorry but role shop can't have more than {self.plugin.data.roleshop.max_roles} roles."
            return await ctx.send_line(res)

        if isinstance(role, str):
            role = await ctx.guild.create_role(name=role, reason=f"Role created for role shop. [{ctx.author}]")
        await ctx.guild_profile.roleshop.create_role(role.id, points)
        await ctx.send_line(f"✅    Added {role.name} to role shop with {points} points.")

    @RoleShopBase.listener()
    async def on_guild_role_delete(self, role):
        guild_profile = await self.bot.guild_cache.get_profile(role.guild.id)
        if roleshop_role := guild_profile.roleshop.roles.get(role.id):
            await guild_profile.roleshop.remove_role(roleshop_role.id)

    @RoleShopBase.role_shop.command(name="remove", aliases=["delete"])
    @has_permissions(manage_roles=True)
    async def delete_role(self, ctx, *, role: typing.Union[discord.Role, int] = None):
        """Remove specified role from the Role Shop.
        It displays an interactive reaction based menu to choose your desired role if it's not specified.

        """
        description = "```css\nDisplaying Role Shop roles. React with respective emote to remove that role.```"

        if not role:
            role = await self._get_role(
                ctx, role, ctx.guild_profile.roleshop.roles, "Delete Menu - Role Shop", description)

        if isinstance(role, int):
            if not ctx.guild_profile.roleshop.roles.get(role):
                raise commands.BadArgument
            role = DeletedRole(role)

        if await ctx.confirm(f"⚠    Are you sure to remove {role.name} from role shop?"):
            # await role.delete(reason=f"Role deleted from role shop. [{ctx.author}]")
            await ctx.guild_profile.roleshop.remove_role(role.id)

            await ctx.send_line(f"✅    {role.name} has been removed from role shop.")

    @RoleShopBase.role_shop.group(name="modify", aliases=["edit"])
    @has_permissions(manage_roles=True)
    async def modify_role(self, ctx):
        """Make changes to existing Role Shop role."""
        pass

    @modify_role.command(name="points", aliases=["point"])
    async def modify_points(self, ctx, new_points: int, *, role: discord.Role = None):
        """Modify points required to redeem or purchase role.
        It displays an interactive reaction based menu to choose your desired role if it's not specified.

        """
        description = "```css\nDisplaying Role Shop roles. React with respective emote to modify that role.```"
        role = await self._get_role(ctx, role, ctx.guild_profile.roleshop.roles, "Modify Menu - Role Shop", description)

        if await ctx.confirm(f"⚠    Are you sure to change points of {role.name} to {new_points}?"):
            await ctx.guild_profile.roleshop.set_points(role.id, new_points)

            await ctx.send_line(f"✅    {role.name} points has been changed to {new_points}.")

    @RoleShopBase.role_shop.command(name="resetall", aliases=["reseteveryone"])
    @has_permissions(administrator=True)
    async def reset_user_points(self, ctx):
        """WARNING: This command will reset everyone's roleshop points. This will not affect already owned roleshop
        roles.

        """
        if not await ctx.confirm():
            return
        if not await ctx.confirm(f"⚠    Are you really sure to reset EVERYONE's roleshop points?"):
            return

        profile = await ctx.fetch_member_profile()
        await profile.reset_everyone_points()
        for profile in self.bot.profile_cache.lfu.values():
            profile.guild_profiles.pop(ctx.guild.id, None)
        await ctx.send_line(f"✅    Everyone's roleshop points has been reset. Let's start fresh!")
