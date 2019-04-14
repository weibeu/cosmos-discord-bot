from discord.ext.commands import has_permissions

from ... import Cog
from .base import Settings


class PrefixSettings(Settings):

    async def __check_prefix(self, ctx, prefix):
        if prefix not in self.bot.configs.cosmos.prefixes:
            return True
        await ctx.send_line("❌    That prefix is already part of default global prefixes.")

    @Cog.group(name="prefix", aliases=["prefixes"], invoke_without_command=True)
    @has_permissions(manage_guild=True)
    async def prefix(self, ctx):
        prefixes = self.cache.prefixes.get(ctx.guild.id)
        if not prefixes:
            return await ctx.send_line(f"{ctx.guild.name} doesn't has any custom prefixes.", ctx.guild.icon_url)
        res = f"{ctx.guild.name} custom prefixes: {prefixes}."
        await ctx.send_line(res, ctx.guild.icon_url)

    @prefix.command(name="set")
    async def set_prefix(self, ctx, prefix):
        if not await self.__check_prefix(ctx, prefix):
            return
        self.cache.prefixes.set(ctx.guild.id, [prefix])
        await self.plugin.collection.update_one(
            {"guild_id": ctx.guild.id}, {"$set": {"prefixes": [prefix]}}
        )
        await ctx.send_line(f"{prefix} has been set as custom prefix of {ctx.guild.name}.", ctx.guild.icon_url)

    @Cog.checks.prime_guild()
    @prefix.command(name="add")
    async def add_prefix(self, ctx, prefix):
        if not await self.__check_prefix(ctx, prefix):
            return
        prefixes = self.cache.prefixes.get(ctx.guild.id, list())
        max_prefixes = self.plugin.data.guild.max_prefixes
        if len(prefixes) >= max_prefixes:
            return await ctx.send_line(f"❌    Sorry but servers can have maximum up-to {max_prefixes} custom prefixes.")
        prefixes.append(prefix)
        self.cache.prefixes.update({ctx.guild.id: prefixes})
        await self.plugin.collection.update_one(
            {"guild_id": ctx.guild.id}, {"$addToSet": {"prefixes": prefix}}
        )
        await ctx.send_line(
            f"{prefix} has been added to list of custom prefixes of {ctx.guild.name}.", ctx.guild.icon_url)

    @prefix.command(name="remove", aliases=["delete"])
    async def remove_prefix(self, ctx, prefix):
        prefixes = self.cache.prefixes.get(ctx.guild.id, list())
        # TODO: Probably add reaction based menu to remove prefixes.
        try:
            prefixes.remove(prefix)
        except ValueError:
            return await ctx.send_line("⚠    Sorry but that prefix is not registered.")
        else:
            await self.plugin.collection.update_one(
                {"guild_id": ctx.guild.id}, {"$addToSet": {"prefixes": prefix}}
            )
        await ctx.send_line(f"✅    Prefix {prefix} has been removed from list of custom prefixes of {ctx.guild.name}.")

    @prefix.command(name="clear", aliases=["clean"])
    async def clear_prefixes(self, ctx):
        # TODO: Add confirm menu here.
        try:
            self.cache.prefixes.pop(ctx.guild.id)
        except KeyError:
            return await ctx.send_line(f"{ctx.guild.name} doesn't has any custom prefixes set.", ctx.guild.icon_url)
        else:
            await self.plugin.collection.update_one({"guild_id": ctx.guild.id}, {"$unset": {"prefixes": ""}})
        await ctx.send_line(f"✅    Cleared all custom prefixes of {ctx.guild.name}.")
