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

from . import base
from aiohttp import web

import hmac


class PatreonHook(base.BaseView):

    ROUTE = "/patreon/"
    TYPE = base.ViewTypes.WEBHOOK

    DISPATCH_EVENT = "patreon_{trigger}"

    async def __authorize(self):
        body = await self.request.read()
        return hmac.compare_digest(
            self.request.headers.get("X-Patreon-Signature", str()),
            hmac.new(self.bot.configs.server.PATREON_WEBHOOK_SECRET.encode(), body, digestmod="md5").hexdigest()
        )

    async def post(self):
        if not await self.__authorize():
            raise web.HTTPForbidden
        trigger = self.request.headers["X-Patreon-Event"].replace(":", "_")
        json = await self.request.json()
        event = self.DISPATCH_EVENT.format(trigger=trigger)
        return web.Response()
