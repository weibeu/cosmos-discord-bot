from .._models import GuildBaseCog

from discord.ext.commands import MissingPermissions


class Settings(GuildBaseCog):

    async def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            raise MissingPermissions(["manage_guild"])
        return True
