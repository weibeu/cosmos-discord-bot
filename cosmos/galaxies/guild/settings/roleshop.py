import typing

import discord

from .base import Settings


class RoleShopSettings(Settings):

    @Settings.roles.group(name="roleshop", aliases=["shop"])
    async def role_shop(self, ctx):
        pass

    @role_shop.command(name="create")
    async def create_role(self, ctx, points: int, *, role: typing.Union[discord.Role, str]):
        # if len(ctx.guild_profile.roleshop) >= self.plugin.data.roleshop.max_roles:
        #     res = f"❌    Sorry but role shop can't have more than {self.plugin.data.roleshop.max_roles} roles."
        #     return await ctx.send_line(res)

        if isinstance(role, str):
            role = await ctx.guild.create_role(name=role, reason=f"Role created for role shop. [{ctx.author}]")
        await ctx.guild_profile.roleshop.create_role(role.id, points)
        await ctx.send_line(f"✅    Added role {role.name} to role shop with {points} points.")
