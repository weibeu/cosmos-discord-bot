from discord.ext.commands import CommandError


class NotEnoughPointsError(CommandError):

    pass


class RoleNotFoundError(CommandError):

    pass
