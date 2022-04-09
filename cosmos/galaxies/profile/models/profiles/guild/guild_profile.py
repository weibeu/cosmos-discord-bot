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

from .roleshop import MemberRoleShop
from .guild_points import GuildPoints
from .experience import MemberExperience


class GuildMemberProfile(GuildPoints, MemberExperience):

    @property
    def profile(self):
        return self._profile

    @property
    def guild_id(self):
        return self._guild_id

    async def fetch_guild_profile(self):
        return await self.plugin.bot.guild_cache.get_profile(self.guild.id)

    @classmethod
    def from_document(cls, profile, guild_id, document: dict):
        return cls(profile, guild_id, **document)

    def __init__(self, profile, guild_id, **kwargs):
        self._profile = profile    # CosmosUserProfile
        GuildPoints.__init__(self, **kwargs)
        MemberExperience.__init__(self, **kwargs)
        self._guild_id = int(guild_id)
        self.roleshop = MemberRoleShop(self, **kwargs)
        self.moderation_logs = kwargs.get("logs", dict()).get("moderation", list())

    def to_update_document(self):
        # self.cache_voice_xp()
        return {
            f"{self.guild_filter}.stats.xp.chat": self.xp,
            f"{self.guild_filter}.stats.xp.voice": self._voice_xp,
            f"{self.guild_filter}.points.points": self.points,
        }

    async def log_moderation(self, _id):
        self.moderation_logs.append(_id)

        await self.collection.update_one(self.document_filter, {
            "$addToSet": {f"{self.guild_filter}.logs.moderation": _id}
        })

    async def clear_moderation_logs(self):
        self.moderation_logs.clear()

        await self.collection.update_one(self.document_filter, {
            "$unset": {f"{self.guild_filter}.logs.moderation": ""}
        })

    async def get_text_rank(self):
        pipeline = [
            {"$match": {
                self.guild_filter: {"$exists": True},
                f"{self.guild_filter}.stats.xp.chat": {"$gt": self.xp}
            }},
            {"$count": "surpassed"}
        ]
        document = await self.collection.aggregate(pipeline).to_list(None)
        try:
            return document[0]["surpassed"] + 1
        except IndexError:
            return 1

    async def get_voice_rank(self):
        pipeline = [
            {"$match": {
                self.guild_filter: {"$exists": True},
                f"{self.guild_filter}.stats.xp.voice": {"$gt": self._voice_xp}
            }},
            {"$count": "surpassed"}
        ]
        document = await self.collection.aggregate(pipeline).to_list(None)
        try:
            return document[0]["surpassed"] + 1
        except IndexError:
            return 1

    async def reset_everyone_xp(self, channel):
        if not self.member.guild_permissions.administrator:
            raise NotImplementedError
        await self.collection.update_many({}, {"$unset": {
            f"{self.guild_filter}.stats.xp.{channel}": ""
        }})

    async def reset_everyone_points(self):
        if not self.member.guild_permissions.administrator:
            raise NotImplementedError
        await self.collection.update_many({}, {"$unset": {
            f"{self.guild_filter}.points.points": ""
        }})
