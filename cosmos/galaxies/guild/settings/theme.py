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

from discord.ext.commands import has_permissions

import discord

from .base import Settings


class ThemeSettings(Settings):
    """A plugin to uniquely customize server's theme."""

    @Settings.group(name="theme", aliases=["themes"])
    async def theme_setting(self, ctx):
        """Configure theme settings."""
        pass

    @theme_setting.group(name="color", aliases=["colour"], invoke_without_command=True)
    async def theme_color(self, ctx):
        """Displays current theme color of the server."""
        if ctx.guild_profile.theme.color:
            res = f"{ctx.guild.name} theme color is set to {ctx.guild_profile.theme.color}."
        else:
            res = f"{ctx.guild.name} theme color isn't set yet."
        return await ctx.send_line(res, ctx.guild.icon_url)

    @Settings.checks.prime_guild()
    @theme_color.command(name="set")
    @has_permissions(manage_guild=True)
    async def set_theme_color(self, ctx, *, color: discord.Color):
        """Set a new theme color for server."""
        await ctx.guild_profile.theme.set_color(color)
        await ctx.send_line(
            f"{ctx.guild.name} theme color has been set to {ctx.guild_profile.theme.color}.", ctx.guild.icon_url
        )

    @theme_color.command(name="remove", aliases=["delete"])
    async def remove_theme_color(self, ctx):
        """Removes the theme color of server which was set previously."""
        if not await ctx.confirm():
            return
        await ctx.guild_profile.theme.remove_color()
        await ctx.send_line(f"{ctx.guild.name} theme color has been removed.", ctx.guild.icon_url)
