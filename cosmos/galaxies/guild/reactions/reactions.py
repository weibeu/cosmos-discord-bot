from discord.ext import commands

from .._models import GuildBaseCog


class Reactions(GuildBaseCog):

    async def cog_check(self, ctx):
        if ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])
        return True

    @GuildBaseCog.group(name="reaction", aliases=["reactions"])
    async def reaction(self, ctx):
        pass
