from ... import Cog, MemberMissingPermissions


class GuildSettingsBase(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            raise MemberMissingPermissions(["manage_guild"])
        return True

    async def cog_before_invoke(self, ctx):
        _ = await self.cache.get_profile(ctx.guild.id)    # Ensure CosmosGuild is in cache before changing its settings.
