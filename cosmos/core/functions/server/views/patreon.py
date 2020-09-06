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


class PatreonUser(object):

    @staticmethod
    def __get_objects(included):
        return {d["type"]: d["attributes"] for d in included if d.get("type")}

    @property
    def discord_id(self):
        try:
            return int(self._objects["user"]["social_connections"]["discord"]["user_id"])
        except KeyError:
            pass

    @property
    def pledge_amount(self):
        try:
            cents = self._objects["tier"]["amount_cents"]
        except KeyError:
            cents = self._pledge_amount
        return cents // 100

    @property
    def tier(self):
        return [t for t in sorted(self.__handler.bot.PrimeTier) if self.pledge_amount >= t.value][-1]

    def __init__(self, handler, data):
        self.__handler = handler
        attrs = data["data"]["attributes"]
        self._objects = self.__get_objects(data.get("included") or [])
        self.is_former = attrs.get("patron_status") == "former_patron"
        self._pledge_amount = attrs.get("will_pay_amount_cents") or attrs.get("currently_entitled_amount_cents")

    async def fetch_cosmos_user_profile(self):
        return await self.__handler.fetch_cosmos_user_profile(self.discord_id)


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
        json = await self.request.json()
        self.bot.log.info(f"Received [{self.NAME}] payload: {json}.")
        trigger = self.request.headers["X-Patreon-Event"].replace(":", "_")
        event = self.DISPATCH_EVENT.format(trigger=trigger)
        self.bot.log.info(f"Dispatching Event [on_{event}].")
        self.bot.dispatch(event, PatreonUser(self, json))
        return web.Response()
