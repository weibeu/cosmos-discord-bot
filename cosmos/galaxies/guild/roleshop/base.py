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
from discord.ext.commands import CommandError

from .._models import GuildBaseCog


class NotRoleShopRoleError(CommandError):

    handled = True

    def __init__(self, role):
        self.role = role


class DeletedRole(discord.Object):

    def __str__(self):
        return "@deleted-role"

    @property
    def name(self):
        return self.__str__()


class RoleShopBase(GuildBaseCog):
    """Base cog for Role Shop plugin."""

    async def _get_role(self, ctx, role, roles, title, description: str = str()) -> discord.Role:
        # roles = roles or ctx.guild_profile.roleshop.roles
        if role:
            if not ctx.guild_profile.roleshop.has_role(role.id):
                raise NotRoleShopRoleError(role)
            return role
        menu = ctx.get_field_menu(roles, self._paginator_parser)
        menu.embed.description = description
        menu.embed.set_author(name=title, icon_url=ctx.author.avatar_url)
        response = await menu.wait_for_response()
        return ctx.guild.get_role(response.entry.id) or DeletedRole(response.entry.id)

    @staticmethod
    async def _paginator_parser(ctx, roleshop_role, _):
        role = ctx.guild.get_role(roleshop_role.id)
        points = roleshop_role.points
        try:
            return role.name, f"`POINTS:` **{points}**\n`COLOR:` {role.mention}"
        except AttributeError:
            return "@deleted-role", f"**POINTS:** `{points}`\n**ID:** `{roleshop_role.id}`"

    @GuildBaseCog.group(name="roleshop", invoke_without_command=True)
    async def role_shop(self, ctx):
        """Displays all of the roles which can be purchased from role shop."""
        if not ctx.guild_profile.roleshop:
            return await ctx.send_line("❌    This server has no roles created or assigned to role shop.")
        paginator = ctx.get_field_paginator(ctx.guild_profile.roleshop.roles, entry_parser=self._paginator_parser)
        paginator.embed.description = "```css\nDisplaying Role Shop roles which can be purchased for specified points" \
                                      ".```"
        paginator.embed.set_author(name="Role Shop", icon_url=ctx.author.avatar_url)
        await paginator.paginate()

    async def cog_command_error(self, ctx, error):    # TODO: Override Command with custom dispatch_error method.
        if isinstance(error, NotRoleShopRoleError):
            await ctx.send_line(
                f"You can't purchase {error.role.name}. It is not a roleshop role.", self.bot.theme.images.cancel)
