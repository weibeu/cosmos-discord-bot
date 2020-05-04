from discord.ext import commands


class NotPrime(commands.CheckFailure):

    message = "Click here to get prime and unlock all features including this."

    def __init__(self, message=str()):
        self.message = message or self.message


class GuildNotPrime(NotPrime):

    ...


class UserNotPrime(NotPrime):

    ...


class DisabledFunctionError(commands.CheckFailure):

    def __init__(self, globally=False):
        self.globally = globally


class CosmosIsDisableError(commands.CheckFailure):

    ...
