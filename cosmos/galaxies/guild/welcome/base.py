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

from ..settings.base import Settings


class WelcomeBase(Settings):

    @Settings.group(name="welcome", aliases=["join"])
    async def welcome(self, ctx):
        """Manage different welcome settings of your server."""
        pass


class MessageTemplateMember(object):

    __slots__ = ("id", "username", "name", "discriminator", "mention")

    def __init__(self, author):
        self.id = author.id
        self.username = str(author)
        self.name = author.name
        self.discriminator = author.discriminator
        self.mention = author.mention

    @property
    def __dict__(self):
        return {
            "id": self.id, "username": self.username, "name": self.name,
            "discriminator": self.discriminator, "mention": self.mention,
        }
