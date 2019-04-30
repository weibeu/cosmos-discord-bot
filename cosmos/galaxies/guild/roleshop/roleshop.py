import discord

from .points import RoleShopPoints
from .settings import RoleShopSettings

from .._models.exceptions import *


class RoleShop(RoleShopPoints, RoleShopSettings):

    @RoleShopSettings.role_shop.command(name="purchased")
    async def purchased_roles(self, ctx):
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        paginator = ctx.get_field_paginator(profile.roleshop.roles, entry_parser=self._paginator_parser)
        await paginator.paginate()

    @RoleShopSettings.role_shop.command(name="buy", aliases=["purchase"])
    async def buy_role(self, ctx, *, role: discord.Role = None):
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in ctx.guild_profile.roleshop.roles if role not in profile.roleshop.roles]
        role = await self._get_role(ctx, role, roles)
        _role = ctx.guild_profile.roleshop.roles.get(role.id)
        if _role in profile.roleshop.roles:
            return await ctx.send_line(f"❌    You have already purchased {role.name}.")
        if await ctx.confirm(f"⚠    Are you sure to purchase {role.name}?"):
            await ctx.guild_profile.roleshop.buy_role(profile, role.id)
            await ctx.send_line(f"✅    {role.name} purchased. Now you're left with {profile.points} guild points.")
            if await ctx.confirm(f"❓    Equip {role.name} right now?"):
                await ctx.author.add_roles(role, reason="Role purchased from role shop.")

    @buy_role.error
    async def buy_error(self, ctx, error):
        if isinstance(error, NotEnoughPointsError):
            return await ctx.send_line("❌    Sorry but you don't have enough guild points to purchase that role.")

    @RoleShopSettings.role_shop.command(name="sell")
    async def sell_role(self, ctx, *, role: discord.Role = None):
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        role = await self._get_role(ctx, role, profile.roleshop.roles)
        _role = ctx.guild_profile.roleshop.roles.get(role.id)
        if _role not in profile.roleshop.roles:
            return await ctx.send_line(f"❌    You haven't purchased {role.name} yet.")
        if await ctx.confirm(f"⚠    Are you sure to sell {role.name}?"):
            await ctx.guild_profile.roleshop.sell_role(profile, role.id)
            await ctx.author.remove_roles(role)
            await ctx.send_line(f"✅    You sold {role.name} earning {_role.points} guild points.")

    @RoleShopSettings.role_shop.group(name="equip", invoke_without_command=True)
    async def equip_role(self, ctx, *, role: discord.Role = None):
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in profile.roleshop.roles if ctx.guild.get_role(role.id) not in ctx.author.roles]
        role = await self._get_role(ctx, role, roles)
        _role = ctx.guild_profile.roleshop.roles.get(role.id)
        if _role not in profile.roleshop.roles:
            return await ctx.send_line(f"❌    You haven't purchased {role.name} yet.")
        if role in ctx.author.roles:
            return await ctx.send_line(f"❌    You've already equipped {role.name}.")
        await ctx.author.add_roles(role, reason="Role equipped from role shop.")
        await ctx.send_line(f"✅    {role.name} equipped.")

    @equip_role.command(name="all")
    async def equip_all_roles(self, ctx):
        if not await ctx.confirm():
            return
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        for _role in profile.roleshop.roles:
            role = ctx.guild.get_role(_role.id)
            await ctx.author.add_roles(role, reason="Role equipped from role shop.")
        await ctx.send_line("✅    Equipped all purchased roles.")

    @RoleShopSettings.role_shop.group(name="unequip", invoke_without_command=True)
    async def unequip_role(self, ctx, *, role: discord.Role = None):
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in profile.roleshop.roles if ctx.guild.get_role(role.id) in ctx.author.roles]
        role = await self._get_role(ctx, role, roles)
        if role not in ctx.author.roles:
            return await ctx.send_line(f"❌    You've already un-equipped {role.name}.")
        await ctx.author.remove_roles(role)
        await ctx.send_line(f"✅    {role.name} un-equipped.")

    @unequip_role.command(name="all")
    async def unequip_all_roles(self, ctx):
        if not await ctx.confirm():
            return
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        for _role in profile.roleshop.roles:
            role = ctx.guild.get_role(_role.id)
            await ctx.author.remove_roles(role, reason="Role un-equipped from role shop.")
        await ctx.send_line("✅    Un-equipped all role shop roles.")
