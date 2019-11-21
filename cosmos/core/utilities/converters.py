from discord.ext import commands


class RoleConvertor(commands.Converter):

    async def convert(self, ctx, argument):
        try:
            return [await commands.RoleConverter().convert(ctx, argument)]
        except commands.BadArgument:
            return [await commands.RoleConverter().convert(ctx, raw_role) for raw_role in argument.split()]
