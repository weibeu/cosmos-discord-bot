from .._models import GuildBaseCog

from discord.ext.commands import MissingPermissions


class Settings(GuildBaseCog):

    async def cog_check(self, ctx):
        await super().cog_check(ctx)
        if not ctx.author.guild_permissions.administrator:
            raise MissingPermissions(["administrator"])
        return True
