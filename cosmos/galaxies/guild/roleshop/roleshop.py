import discord

from .points import RoleShopPoints
from .settings import RoleShopSettings

from .._models.exceptions import *


class RoleShop(RoleShopPoints, RoleShopSettings):
    """Implements Role Shop functionality in server.

    Members can redeem or purchase roles which has been put on Role Shop by server administrators using their
    Guild Points. Once the role is redeemed it stays in their inventory. They can easily equip or un-equip any of the
    roles they have redeemed previously.

    """

    INESCAPABLE = False

    @RoleShopSettings.role_shop.command(name="purchased", inescapable=False)
    async def purchased_roles(self, ctx, *, member: discord.Member = None):
        """Displays your all of the roles purchased from Role Shop or of specified member."""
        member = member or ctx.author
        profile = await self.bot.profile_cache.get_guild_profile(member.id, ctx.guild.id)
        paginator = ctx.get_field_paginator(profile.roleshop.roles, entry_parser=self._paginator_parser)
        paginator.embed.set_author(name="Purchased Roles - Role Shop", icon_url=ctx.author.avatar_url)
        paginator.embed.description = "```css\nDisplaying roles you have purchased from Role Shop.```"
        await paginator.paginate()

    @RoleShopSettings.role_shop.command(name="buy", aliases=["purchase"], inescapable=False)
    async def buy_role(self, ctx, *, role: discord.Role = None):
        """Redeem or purchase specified role from Role Shop using your earned Guild Points.
        It displays an interactive reaction based menu to choose your desired role if it's not specified.

        """
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in ctx.guild_profile.roleshop.roles if role not in profile.roleshop.roles]
        # TODO: Maybe only include roles which can be purchased by that member because of less points.
        description = "```css\nDisplaying Role Shop roles which you can purchase using your earned points. React " \
                      "with the respective emote to purchase the same role.```"
        role = await self._get_role(ctx, role, roles, "Buy Menu - Role Shop", description)
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

    # @RoleShopSettings.role_shop.command(name="sell", inescapable=False)
    # async def sell_role(self, ctx, *, role: discord.Role = None):
    #     """Sell your already purchased role back to Role Shop giving you Guild Points worth value of same role."""
    #     # TODO: Let Guild Administrators decide if members can sell role.
    #     profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
    #     role = await self._get_role(ctx, role, profile.roleshop.roles)
    #     _role = ctx.guild_profile.roleshop.roles.get(role.id)
    #     if _role not in profile.roleshop.roles:
    #         return await ctx.send_line(f"❌    You haven't purchased {role.name} yet.")
    #     if await ctx.confirm(f"⚠    Are you sure to sell {role.name}?"):
    #         await ctx.guild_profile.roleshop.sell_role(profile, role.id)
    #         await ctx.author.remove_roles(role)
    #         await ctx.send_line(f"✅    You sold {role.name} earning {_role.points} guild points.")

    @RoleShopSettings.role_shop.group(name="equip", invoke_without_command=True, inescapable=False)
    async def equip_role(self, ctx, *, role: discord.Role = None):
        """Equip specified role which you have purchased from the Role Shop.
        It displays an interactive reaction based menu to choose your desired role if it's not specified.

        """
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in profile.roleshop.roles if ctx.guild.get_role(role.id) not in ctx.author.roles]
        description = "```css\nDisplaying your purchased roles from Role Shop which aren't equipped. React with " \
                      "the respective emote to equip that role.```"
        role = await self._get_role(ctx, role, roles, "Equip Menu - Role Shop", description)
        _role = ctx.guild_profile.roleshop.roles.get(role.id)
        if _role not in profile.roleshop.roles:
            return await ctx.send_line(f"❌    You haven't purchased {role.name} yet.")
        if role in ctx.author.roles:
            return await ctx.send_line(f"❌    You've already equipped {role.name}.")
        await ctx.author.add_roles(role, reason="Role equipped from role shop.")
        await ctx.send_line(f"✅    {role.name} equipped.")

    @equip_role.command(name="all")
    async def equip_all_roles(self, ctx):
        """Equip all of the roles you have purchased from Role Shop."""
        if not await ctx.confirm():
            return
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        for _role in profile.roleshop.roles:
            role = ctx.guild.get_role(_role.id)
            await ctx.author.add_roles(role, reason="Role equipped from role shop.")
        await ctx.send_line("✅    Equipped all purchased roles.")

    @RoleShopSettings.role_shop.group(name="unequip", invoke_without_command=True, inescapable=False)
    async def unequip_role(self, ctx, *, role: discord.Role = None):
        """Un-equip specified Role Shop role which you have already equipped."""
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in profile.roleshop.roles if ctx.guild.get_role(role.id) in ctx.author.roles]
        description = "```css\nDisplaying your purchased roles from Role Shop which are equipped. React with " \
                      "the respective emote to un-equip that role.```"
        role = await self._get_role(ctx, role, roles, "Un Equip Menu - Role Shop", description)
        if role not in ctx.author.roles:
            return await ctx.send_line(f"❌    You've already un-equipped {role.name}.")
        await ctx.author.remove_roles(role)
        await ctx.send_line(f"✅    {role.name} un-equipped.")

    @unequip_role.command(name="all")
    async def unequip_all_roles(self, ctx):
        """Un-equip all of the roles belonging to Role Shop which you have equipped."""
        if not await ctx.confirm():
            return
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        for _role in profile.roleshop.roles:
            role = ctx.guild.get_role(_role.id)
            await ctx.author.remove_roles(role, reason="Role un-equipped from role shop.")
        await ctx.send_line("✅    Un-equipped all role shop roles.")
