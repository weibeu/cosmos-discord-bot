from discord.ext import commands

from .._models import GuildBaseCog


class Reactions(GuildBaseCog):
    """This plugin provides reaction based utilities."""

    async def cog_check(self, ctx):
        await super().cog_check(ctx)
        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])
        return True

    @GuildBaseCog.group(name="reaction", aliases=["reactions"])
    async def reaction(self, ctx):
        """It contains multiple reaction based sub-commands."""
        pass
