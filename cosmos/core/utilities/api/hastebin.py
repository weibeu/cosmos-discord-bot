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

import aiohttp


class HasteBinURL(object):

    BASE = "https://hastebin.com/"

    def __init__(self, response_key):
        self._response_key = response_key

    @property
    def url(self):
        return self.BASE + self._response_key

    @property
    def py(self):
        return self.url + ".py"

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url


class HasteBin(object):

    BASE_URL = "https://hastebin.com/documents"
    ENCODING = "utf-8"

    async def haste(self, content: str) -> HasteBinURL:
        content = str(content)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.BASE_URL, data=content.encode(self.ENCODING)) as post:
                response = await post.json()
                return HasteBinURL(response["key"])
