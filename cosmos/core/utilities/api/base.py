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

import abc
import aiohttp


class APIHTTPExceptionBase(Exception):

    pass


class _APIMeta(type):

    pass


class BaseAPIHTTPClient(object, metaclass=_APIMeta):

    API_BASE_URL = str()
    BASE_EXCEPTION = APIHTTPExceptionBase

    def __init__(self, client):
        self.client = client
        self.session = aiohttp.ClientSession()

    def __new__(cls, *args, **kwargs):
        if not cls.API_BASE_URL:
            raise ValueError(f"No API_BASE_URL specified in class {cls}.")

    @abc.abstractmethod
    def _get_headers(self):
        return dict()

    async def request(self, route, method="POST", data=None, **kwargs):
        url = f"{self.API_BASE_URL}{route}"
        async with self.session.request(
            method=method, url=url, data=data, headers=self._get_headers(), **kwargs
        ) as response:
            if response.status >= 400:
                raise self.BASE_EXCEPTION(
                    f"[{self.__class__.__name__}] API server response with status code: {response.status}."
                )
            return response
