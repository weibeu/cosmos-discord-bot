import discord
from discord.ext.commands import CommandError

from .._models import GuildBaseCog


class NotRoleShopRoleError(CommandError):

    def __init__(self, role):
        self.role = role


class RoleShopBase(GuildBaseCog):

    async def _get_role(self, ctx, role=None) -> discord.Role:
        if role:
            if not ctx.guild_profile.roleshop.has_role(role.id):
                raise NotRoleShopRoleError(role)
            return role
        menu = ctx.get_field_menu(ctx.guild_profile.roleshop.roles, self.__paginator_parser)
        response = await menu.wait_for_response()
        return ctx.guild.get_role(response.entry.id)

    @staticmethod
    async def __paginator_parser(ctx, roleshop_role, _):
        role = ctx.guild.get_role(roleshop_role.id)
        points = roleshop_role.points
        return role.name, f"{ctx.bot.emotes.misc.coins} {points}"

    @GuildBaseCog.group(name="roleshop")
    async def role_shop(self, ctx):
        pass

    @role_shop.error
    async def role_shop_error(self, ctx, error):    # TODO: Override Command with custom dispatch_error method.
        if isinstance(error, NotRoleShopRoleError):
            await ctx.send_line(f"❌    {error.role.name} is not a role shop role.")
