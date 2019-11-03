from discord.ext import commands


class GuildNotPrime(commands.CheckFailure):

    pass


class UserNotPrime(commands.CheckFailure):

    pass


class FunctionDisabledError(commands.CheckFailure):

    pass
