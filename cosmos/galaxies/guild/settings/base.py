from ... import Cog

from discord.ext.commands import MissingPermissions, has_permissions


class Settings(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    # def cog_check(self, ctx):
    #     if not ctx.author.guild_permissions.manage_guild:
    #         raise MissingPermissions(["manage_guild"])
    #     return True

    async def cog_before_invoke(self, ctx):
        ctx.guild_profile = await self.cache.get_profile(ctx.guild.id)
        # Ensure CosmosGuild is in cache before changing its settings and dynamically pass it to ctx.guild_profile.

    @has_permissions(manage_guild=True)
    @Cog.group(name="welcome", aliases=["join"])
    async def welcome(self, ctx):
        pass
