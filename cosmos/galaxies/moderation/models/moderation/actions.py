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

class ActionBaseMeta(type):

    auto = False
    TITLE = str()

    def __str__(self):
        if self.auto:
            return f"[Auto] {self.TITLE}"
        return self.TITLE


class ActionsBase(metaclass=ActionBaseMeta):

    TITLE = str()

    def __init__(self, auto=False):
        self.auto = auto

    @property
    def __name__(self):
        if self.auto:
            return f"[Auto] {self.__class__.__name__}"
        return self.__class__.__name__

    def __str__(self):
        if self.auto:
            return f"[Auto] {self.TITLE}"
        return self.TITLE


class Warned(ActionsBase):

    TITLE = "Member Warned"


class Kicked(ActionsBase):

    TITLE = "Member Kicked"


class Banned(ActionsBase):

    TITLE = "User Banned"


class Unbanned(ActionsBase):

    TITLE = "User Unbanned"


class Muted(ActionsBase):

    TITLE = "Member Muted"


class UnMuted(ActionsBase):

    TITLE = "Member Unmuted"
