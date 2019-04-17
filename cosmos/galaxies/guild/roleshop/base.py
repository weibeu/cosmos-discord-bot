from discord.ext.commands import has_permissions

from .._models import GuildBaseCog


class RoleShopBase(GuildBaseCog):

    @GuildBaseCog.group(name="roleshop")
    @has_permissions(manage_roles=True)
    async def role_shop(self, ctx):
        pass
