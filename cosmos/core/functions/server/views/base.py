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

from abc import ABCMeta
from enum import Enum
from aiohttp import web


class ViewTypes(Enum):

    ANY = "/"
    WEBHOOK = "/webhooks"


class ViewsMeta(ABCMeta):

    NAME = str()
    ROUTE = str()
    TYPE = ViewTypes.ANY

    def __init__(cls, name, *args, **kwargs):
        if name != "BaseView":
            if not cls.ROUTE:
                raise ValueError("A view must have valid ROUTE attribute.")
            cls.ROUTE = cls.TYPE.value + cls.ROUTE
            cls.NAME = cls.NAME.upper() or cls.__name__.upper()
        super().__init__(name, *args, **kwargs)


class BaseView(web.View, metaclass=ViewsMeta):

    HEADER = "Authorization"
    DISPATCH_EVENT = str()

    @property
    def bot(self):
        return self.request.app["COSMOS"]

    async def fetch_cosmos_user_profile(self, user_id):
        return await self.bot.profile_cache.get_profile(user_id)
