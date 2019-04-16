import discord
import typing

from .base import Settings


class RoleShopSettings(Settings):

    @Settings.roles.group(name="shop", aliases=["roleshop"])
    async def role_shop(self, ctx):
        pass

    async def __get_role(self, ctx, role=None) -> discord.Role:
        if role:
            if not ctx.guild_profile.roleshop.has_role(role.id):
                await ctx.send_line(f"❌    {role.name} is not a role shop role.")
                raise LookupError
            return role
        menu = ctx.get_field_menu(ctx.guild_profile.roleshop.roles, self.__paginator_parser)
        response = await menu.wait_for_response()
        return ctx.guild.get_role(response.entry.id)

    @staticmethod
    async def __paginator_parser(ctx, roleshop_role, _):
        role = ctx.guild.get_role(roleshop_role.id)
        points = roleshop_role.points
        return role.name, f"{ctx.bot.emotes.misc.coins} {points}"

    @role_shop.command(name="create")
    async def create_role(self, ctx, points: int, *, role: typing.Union[discord.Role, str]):
        if len(ctx.guild_profile.roleshop.roles) >= self.plugin.data.roleshop.max_roles:
            res = f"❌    Sorry but role shop can't have more than {self.plugin.data.roleshop.max_roles} roles."
            return await ctx.send_line(res)

        if isinstance(role, str):
            role = await ctx.guild.create_role(name=role, reason=f"Role created for role shop. [{ctx.author}]")
        await ctx.guild_profile.roleshop.create_role(role.id, points)
        await ctx.send_line(f"✅    Added {role.name} to role shop with {points} points.")

    @role_shop.command(name="remove", aliases=["delete"])
    async def delete_role(self, ctx, *, role: discord.Role = None):
        role = await self.__get_role(ctx, role)

        if await ctx.confirm(f"⚠    Are you sure to remove {role.name} from role shop?"):
            await role.delete(reason=f"Role deleted from role shop. [{ctx.author}]")
            await ctx.guild_profile.roleshop.remove_role(role.id)

            await ctx.send_line(f"✅    {role.name} has been removed from role shop.")

    @role_shop.group(name="modify", aliases=["edit"])
    async def modify_role(self, ctx):
        pass

    @modify_role.command(name="points", aliases=["point"])
    async def modify_points(self, ctx, new_points: int, *, role: discord.Role = None):
        role = await self.__get_role(ctx, role)

        if await ctx.confirm(f"⚠    Are you sure to change points of {role.name} to {new_points}?"):
            await ctx.guild_profile.roleshop.set_points(role.id, new_points)

            await ctx.send_line(f"✅    {role.name} points has been changed to {new_points}.")
