from discord.ext import commands


class RoleConvertor(commands.Converter):

    async def convert(self, ctx, argument):
        try:
            return [await commands.RoleConverter().convert(ctx, argument)]
        except commands.BadArgument:
            return [await commands.RoleConverter().convert(ctx, raw_role) for raw_role in argument.split()]


class CosmosGuildConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (guild := ctx.bot.get_guild(int(argument))):
            raise commands.BadArgument
        return await ctx.bot.guild_cache.get_profile(guild.id)


class CosmosUserProfileConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (user := await commands.UserConverter().convert(ctx, argument)):
            raise commands.BadArgument
        return await ctx.bot.profile_cache.get_profile(user.id)
