from discord.ext import commands


class GuildNotPrime(commands.CheckFailure):

    pass


class UserNotPrime(commands.CheckFailure):

    pass


class DisabledFunctionError(commands.CheckFailure):

    pass
