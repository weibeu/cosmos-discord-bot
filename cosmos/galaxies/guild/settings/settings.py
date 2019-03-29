from ... import Cog, MemberMissingPermissions


class GuildSettings(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            raise MemberMissingPermissions(["manage_guild"])
        return True

    @Cog.group(name="prefix", aliases=["prefixes"], invoke_without_command=True)
    async def prefix(self, ctx):
        prefixes = self.bot.guilds_prefixes.get(ctx.guild.id)
        if not prefixes:
            return await ctx.send_line(f"❌    {ctx.guild.name} doesn't has any custom prefixes.")
        res = f"{ctx.guild.name} custom prefixes: {', '.join(prefixes)}."
        await ctx.send_line(res, ctx.guild.icon_url)
