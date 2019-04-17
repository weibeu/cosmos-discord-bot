from discord.ext.commands import has_permissions, CommandError

from .._models import GuildBaseCog


class NotRoleShopRoleError(CommandError):

    def __init__(self, role):
        self.role = role


class RoleShopBase(GuildBaseCog):

    @GuildBaseCog.group(name="roleshop")
    @has_permissions(manage_roles=True)
    async def role_shop(self, ctx):
        pass

    @role_shop.error
    async def role_shop_error(self, ctx, error):
        if isinstance(error, NotRoleShopRoleError):
            await ctx.send_line(f"❌    {error.role.name} is not a role shop role.")
