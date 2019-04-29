import discord

from .points import RoleShopPoints
from .settings import RoleShopSettings


class RoleShop(RoleShopPoints, RoleShopSettings):

    @RoleShopSettings.role_shop.command(name="buy", aliases=["purchase"])
    async def buy_role(self, ctx, role: discord.Role = None):
        roleshop = ctx.guild_profile.roleshop


    @buy_role.error
    async def buy_error(self, ctx, error):
        if isinstance(error, TypeError):
            return await ctx.send_line("❌    Sorry but you don't have enough guild points to purchase that role.")
