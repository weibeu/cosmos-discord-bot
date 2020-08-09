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

import discord
import datetime


class ModerationAction(object):

    def __init__(self, guild_profile, target, moderator, action_type, reason=None):
        self.guild_profile = guild_profile
        self.bot = self.guild_profile.plugin.bot
        self.target = target
        self.moderator = moderator
        self.action_type = action_type
        self.reason = reason or "Reason not specified."

    @property
    def document(self):
        _ = {
            "action_type": self.action_type.__name__,
            "moderator_id": self.moderator.id,
            "reason": self.reason,
        }
        try:
            _["target_id"] = self.target.id
        except AttributeError:
            _["target_id"] = self.target
        return _

    async def dispatch(self, title):
        self.bot.dispatch("moderation", self)
        if self.target.bot:
            return
        _ = self.bot.theme.embeds.one_line.primary(title)
        _.description = f"**Reason:** {self.reason}"
        _.timestamp = datetime.datetime.now()
        try:
            profile = await self.guild_profile.fetch_member_profile(self.target.id)
        except AttributeError:
            profile = await self.guild_profile.fetch_member_profile(self.target)
        _id = await self.bot.discordDB.set(self.document)
        await profile.log_moderation(_id)
        try:
            return await self.target.send(embed=_)
        except (discord.Forbidden, AttributeError):
            pass
