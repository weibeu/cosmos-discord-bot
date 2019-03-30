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

    async def cog_before_invoke(self, ctx):
        _ = await self.cache.get_profile(ctx.guild.id)    # Ensure CosmosGuild is in cache before changing its settings.

    async def __check_prefix(self, ctx, prefix):
        if prefix not in self.bot.configs.cosmos.prefixes:
            return True
        await ctx.send_line("❌    That prefix is already part of default global prefixes.")

    @Cog.group(name="prefix", aliases=["prefixes"], invoke_without_command=True)
    async def prefix(self, ctx):
        prefixes = self.cache.prefixes.get(ctx.guild.id)
        if not prefixes:
            return await ctx.send_line(f"{ctx.guild.name} doesn't has any custom prefixes.", ctx.guild.icon_url)
        res = f"{ctx.guild.name} custom prefixes: {prefixes}."
        await ctx.send_line(res, ctx.guild.icon_url)

    @prefix.command(name="set", ignore_extra=False)
    async def set_prefix(self, ctx, prefix):
        if not await self.__check_prefix(ctx, prefix):
            return
        self.cache.prefixes.set(ctx.guild.id, [prefix])
        await self.plugin.collection.update_one(
            {"guild_id": ctx.guild.id}, {"$set": {"prefixes": [prefix]}}
        )
        await ctx.send_line(f"{prefix} has been set as custom prefix of {ctx.guild.name}.", ctx.guild.icon_url)

    @prefix.command(name="add", ignore_extra=False)
    async def add_prefix(self, ctx, prefix):
        if not await self.__check_prefix(ctx, prefix):
            return
        prefixes = self.cache.prefixes.get(ctx.guild.id, list())
        max_prefixes = self.plugin.data.guild.max_prefixes
        if len(prefixes) >= max_prefixes:
            return await ctx.send_line(f"❌    Sorry but servers can have maximum upto {max_prefixes} custom prefixes.")
        prefixes.append(prefix)
        self.cache.prefixes.update({ctx.guild.id: prefixes})
        await self.plugin.collection.update_one(
            {"guild_id": ctx.guild.id}, {"$addToSet": {"prefixes": prefix}}
        )
        await ctx.send_line(
            f"{prefix} has been added to list of custom prefixes of {ctx.guild.name}.", ctx.guild.icon_url)
