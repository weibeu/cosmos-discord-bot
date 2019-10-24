from discord.ext.commands import Command, Group, command


class CosmosCommand(Command):

    def __init__(self, *args, **kwargs):
        self.disabled_channels = []
        super().__init__(*args, **kwargs)


class CosmosGroupCommand(Group):

    def __init__(self, *args, **kwargs):
        self.disabled_channels = []
        super().__init__(*args, **kwargs)


def cosmos_command(name: str = None, **attrs):
    return command(name=name, cls=CosmosCommand, **attrs)
    # def decorator(function):
    #     return command(name=name, cls=CosmosCommand, **attrs)(function)
    #
    # return decorator


def cosmos_group_command(name: str = None, **attrs):
    attrs.setdefault('cls', CosmosGroupCommand)
    return cosmos_command(name=name, **attrs)
