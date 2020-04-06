from discord.ext import commands

from ...exceptions import GuildNotPrime


class CosmosChecks(object):

    @classmethod
    def prime_guild(cls):
        async def predicate(ctx):
            if not (await ctx.bot.guild_cache.get_profile(ctx.guild.id)).is_prime:
                raise GuildNotPrime
            return True
        return commands.check(predicate)

    @classmethod
    def check_user(cls, user_id):
        async def predicate(ctx):
            if ctx.author.id == user_id:
                return True
            return False

        return commands.check(predicate)
