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

import typing
import discord

from ... import Cog

from discord.ext import commands
from cosmos.core.utilities import converters


class AdministratorSettings(Cog):
    """Manage important configuration and settings of server."""

    PRESET_COMMANDS = [
        "kick",
        "ban",
        "serverboost",
    ]

    async def cog_check(self, ctx):
        await super().cog_check(ctx)
        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])
        return True

    @Cog.group(name="moderators", aliases=["moderator", "mod", "mods"], invoke_without_command=True)
    async def moderators(self, ctx):
        """Displays list of roles and members who has been assigned as special moderators who can use all of the
        commands from Moderation plugin and more.

        """
        guild_profile = await ctx.fetch_guild_profile()
        roles = [ctx.guild.get_role(_id).mention for _id in guild_profile.moderators if ctx.guild.get_role(_id)]
        members = [ctx.guild.get_member(_id).mention for _id in guild_profile.moderators if ctx.guild.get_member(_id)]
        embed = ctx.embeds.one_line.primary(f"{ctx.guild.name} Moderators", ctx.guild.icon_url)
        embed.description = "```css\nDisplaying roles and members assigned as special moderators of the server.```"
        if roles:
            embed.add_field(name="Moderator Roles", value=" ".join(roles))
        if members:
            embed.add_field(name="Moderator Members", value=" ".join(members))
        if not (roles or members):
            embed.description = f"No special roles or members are assigned yet for {ctx.guild.name} moderators."
        await ctx.send(embed=embed)

    @moderators.command(name="add")
    async def add_moderator(self, ctx, *, moderator: typing.Union[discord.Role, discord.Member]):
        """Adds any role or member as special moderators who can use commands from Moderation plugin and more."""
        if not await ctx.confirm():
            return
        guild_profile = await ctx.fetch_guild_profile()
        if moderator.id in guild_profile.moderators:
            return await ctx.send_line(f"❌    {moderator.name} already exists in server's moderators.")

        await guild_profile.add_moderator(moderator.id)
        await ctx.send_line(f"✅    {moderator.name} has been added to server's moderators.")

    @moderators.command(name="remove")
    async def remove_moderator(self, ctx, *, moderator: typing.Union[discord.Role, discord.Member]):
        """Removes any role or member from special moderators."""
        if not await ctx.confirm():
            return
        guild_profile = await ctx.fetch_guild_profile()
        if moderator.id not in guild_profile.moderators:
            return await ctx.send_line("❌    They are not server's moderator yet.")

        await guild_profile.remove_moderator(moderator.id)
        await ctx.send_line(f"✅    {moderator.name} has been removed from server's moderators.")

    @Cog.group(name="preset", aliases=["presets"], invoke_without_command=True)
    async def preset(self, ctx, command_name, image_url, *, text=None):
        """Sets preset for commands to display certain preset message including images or files every time these
        commands are used.

        Commands supporting presets:
            - kick
            - ban
            - serverboost

        """
        if command_name.lower() not in self.PRESET_COMMANDS:
            return await ctx.send_line(f"❌    Sorry but preset for command {command_name} isn't available yet.")
        guild_profile = await ctx.fetch_guild_profile()
        await guild_profile.set_preset(
            command_name.lower(), image_url=image_url, text=text
        )
        await ctx.send_line(f"✅    Provided presets has been set for {command_name} command.")

    @preset.command(name="serverboost", aliases=["serverboosts"])
    async def server_boost(self, ctx, *, message):
        """Set customized preset message for loggers when someone boosts the server."""
        guild_profile = await ctx.fetch_guild_profile()
        await guild_profile.set_preset("serverboost", message=message)
        await ctx.send_line(f"✅    Preset message for server boost loggers has been set.")

    @preset.command(name="remove", aliases=["clear", "delete"])
    async def remove_preset(self, ctx, command_name):
        """Removes any preset if it was set for specified command."""
        if command_name.lower() not in self.PRESET_COMMANDS:
            return await ctx.send_line(f"❌    Sorry but preset for command {command_name} isn't available yet.")
        guild_profile = await ctx.fetch_guild_profile()
        await guild_profile.remove_preset(command_name)
        await ctx.send_line(f"✅    Presets has been removed from {command_name} command.")

    @Cog.checks.prime_user()
    @Cog.command(name="makeprime", aliases=["claimprime", "redeemprime"])
    async def make_prime(self, ctx, server: converters.CosmosGuildConverter = None):
        """Command to grant prime membership to any of the servers you're administrator of.
        You must already have a valid prime subscription before using this command. This same prime tier
        will get linked to specified server. Assumes current server if no server is explicitly specified.

        """
        user = await ctx.fetch_cosmos_user_profile()
        server = server or await ctx.fetch_guild_profile()
        if not await ctx.confirm(f"Are you sure to link your prime with {server.guild.name}?"):
            return
        await user.make_prime(tier=user.prime_tier, guild_id=server.id)
        await ctx.send_line(f"🎉    {server.guild.name} has been given prime.")
