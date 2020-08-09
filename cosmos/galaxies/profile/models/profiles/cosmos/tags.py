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

from abc import ABC

from ..base import ProfileModelsBase


class Tag(object):

    def __init__(self, name, content):
        self.name = name
        self.content = content

    @property
    def document(self):
        return {
            "name": self.name,
            "content": self.content
        }


class UserTags(ProfileModelsBase, ABC):

    def __init__(self, documents):
        self.tags = [Tag(_["name"], _["content"]) for _ in documents]

    def get_tag(self, name):
        try:
            return [tag for tag in self.tags if tag.name.lower() == name.lower()][0]
        except IndexError:
            pass

    def __remove_tag(self, name):
        tag = self.get_tag(name)
        self.tags.remove(tag)

    async def create_tag(self, name, content):
        if self.get_tag(name):
            await self.remove_tag(name)  # Pull if already exists.
        tag = Tag(name, content)
        self.tags.append(tag)

        await self.collection.update_one(
            self.document_filter, {"$addToSet": {"tags": tag.document}}
        )

    async def remove_tag(self, name):
        self.__remove_tag(name)

        await self.collection.update_one(
            self.document_filter, {"$pull": {"tags": {"$or": [{"name": name}, {"name": name.lower()}]}}}
        )
