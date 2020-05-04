from discord.ext.commands import CommandError


class GuildExceptions(CommandError):

    handled = True

    def __init__(self, handled=None):
        self.handled = handled or self.handled


class NotEnoughPointsError(GuildExceptions):

    pass


class RoleNotFoundError(GuildExceptions):

    pass


class FunctionIsInescapable(GuildExceptions):

    ...
