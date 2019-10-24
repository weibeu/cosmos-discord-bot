from discord.ext.commands import Command, Group


class CosmosCommand(Command):

    def __init__(self, inescapable, *args, **kwargs):
        if not inescapable:
            self.disabled_channels = []
        self.inescapable = inescapable
        super().__init__(*args, **kwargs)


class CosmosGroupCommand(Group):

    def __init__(self, *args, **kwargs):
        self.disabled_channels = []
        super().__init__(*args, **kwargs)


def cosmos_command(name: str = None, inescapable=True, cls=None, **attrs):

    cls = cls or CosmosCommand

    def decorator(function):
        if isinstance(function, CosmosCommand):
            raise TypeError('Callback is already a command.')
        return cls(function, name=name, inescapable=inescapable, **attrs)

    return decorator


def cosmos_group_command(name: str = None, inescapable=True, **attrs):
    attrs.setdefault('cls', CosmosGroupCommand)
    return cosmos_command(name=name, inescapable=inescapable, **attrs)
