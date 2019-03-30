from discord.ext import commands


class GuildNotPrime(commands.CheckFailure):

    pass


class MemberNotPrime(commands.CheckFailure):

    pass


class MemberMissingPermissions(commands.MissingPermissions):

    pass
