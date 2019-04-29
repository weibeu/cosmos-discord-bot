import discord

from .points import RoleShopPoints
from .settings import RoleShopSettings

from .._models.exceptions import *


class RoleShop(RoleShopPoints, RoleShopSettings):

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
