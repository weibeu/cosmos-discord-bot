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

from enum import Enum
from aiohttp import web
from abc import ABCMeta


class ViewTypes(Enum):

    ANY = "/"
    WEBHOOK = "/webhooks"


class __ViewsMeta(ABCMeta):

    TYPE = ViewTypes.ANY
    ROUTE = str()

    def __init__(cls, name, *args, **kwargs):
        if name != "BaseView":
            if not cls.ROUTE:
                raise ValueError("A view must have valid ROUTE attribute.")
            cls.ROUTE = cls.TYPE.value + cls.ROUTE
        super().__init__(name, *args, **kwargs)


class BaseView(web.View, metaclass=__ViewsMeta):

    pass
