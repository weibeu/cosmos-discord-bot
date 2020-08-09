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

from .actions import AutoModerationActions


__triggers__ = [
    "links",
    "spoilers",
    "emoji_spam",
    "banned_words",
    "mass_mentions",
    "discord_invites",
]


class AutoModerationTrigger(object):

    def __init__(self, guild_profile, **_document):
        self.profile = guild_profile
        self._document = _document
        self.name = self._document["name"]
        self._actions = self._document["actions"]
        self.__fetch_special_attributes()
        self.__actions = AutoModerationActions(self)

    def __fetch_special_attributes(self):
        if self.name == "banned_words":
            self.words = set(self._document.get("words", list()))

    @property
    def actions(self):
        return [getattr(self.__actions, _) for _ in self._actions]

    @actions.setter
    def actions(self, value):
        self._actions.append(value)

    def __getattr__(self, item):
        try:
            return self._document[item]
        except KeyError:
            raise AttributeError

    @property
    def title(self):
        return self.name.replace("_", " ").title()

    async def dispatch(self, **kwargs):
        for action in self.actions:
            try:
                await action(**kwargs)
            except AttributeError:
                pass

    @property
    def document(self):
        return {
            "name": self.name,
            "actions": self._actions,
        }


_base = AutoModerationTrigger
