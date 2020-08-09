"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from discord.ext.commands import Command, Group


class CosmosCommand(Command):

    FUNCTION = "commands"

    def __init__(self, function, inescapable=True, **kwargs):
        if not inescapable:
            self.disabled_channels = set()
        self.inescapable = inescapable
        super().__init__(function, **kwargs)


class CosmosGroupCommand(Group):

    FUNCTION = "commands"

    def __init__(self, *args, inescapable=True, **kwargs):
        if not inescapable:
            self.disabled_channels = set()
        self.inescapable = inescapable
        super().__init__(*args, **kwargs)


def cosmos_command(name: str = None, cls=None, **attrs):

    cls = cls or CosmosCommand

    def decorator(function):
        if isinstance(function, CosmosCommand):
            raise TypeError('Callback is already a command.')
        return cls(function, name=name, **attrs)

    return decorator


def cosmos_group_command(name: str = None, **attrs):
    attrs.setdefault('cls', CosmosGroupCommand)
    return cosmos_command(name=name, **attrs)
