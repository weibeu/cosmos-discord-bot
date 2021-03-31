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

from .. import Cog


class _Levels(Cog):
    """This plugin implements experience points and levelling features."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    def __is_ignored(self, message):
        if message.author.id == self.bot.user.id:
            return True
        if message.author.bot:
            return True
        if not message.guild:
            return True

    @Cog.listener()
    async def on_message(self, message):
        if self.__is_ignored(message):
            return

        await self.cache.give_assets(message)

    @staticmethod
    def get_vc_members(voice_channel):
        try:
            return [m for m in voice_channel.members if not m.bot]
        except AttributeError:
            return []

    @staticmethod
    def valid_members(members: list) -> list:
        return [m for m in members if
                not m.voice.self_deaf and
                not m.voice.mute and
                not m.voice.deaf and
                not m.voice.self_mute and
                not m.voice.afk]

    async def get_guild_profile(self, member_id, guild_id):
        profile = await self.cache.get_profile(member_id)
        return await profile.get_guild_profile(guild_id)

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        guild_profile = await self.get_guild_profile(member.id, member.guild.id)

        # user leaving a channel
        if not after.channel and before.channel:
            guild_profile.close_voice_activity()
            guild_profile.profile.close_voice_activity()
            if len(members := self.get_vc_members(before.channel)) > 0:
                if len(valid_members := self.valid_members(members)) < 2:
                    for m in valid_members:
                        gp = await self.get_guild_profile(m.id, member.guild.id)
                        gp.close_voice_activity()
                        gp.profile.close_voice_activity()

        # user channel hopping / mute-unmute etc.
        if before.channel and after.channel:
            # mute-unmute etc.
            if before.channel == after.channel:
                # if did mute-deaf, stop xp
                if ((not before.mute and after.mute) or
                    (not before.deaf and after.deaf) or
                    (not before.self_mute and after.self_mute) or
                        (not before.self_deaf and after.self_mute)):
                    guild_profile.close_voice_activity()
                    guild_profile.profile.close_voice_activity()
                    # if old channel dont have enough members, stop their xp
                    if len(valid_members := self.valid_members(self.get_vc_members(before.channel))) < 2:
                        for m in valid_members:
                            gp = await self.get_guild_profile(m.id, member.guild.id)
                            gp.close_voice_activity()
                            gp.profile.close_voice_activity()

                # if did unmute-undeaf
                elif ((before.mute and not after.mute) or
                      (before.deaf and not after.deaf) or
                      (before.self_mute and not after.self_mute) or
                        (before.self_deaf and not after.self_mute)):
                    # if channel now has enough valid members, start their xp
                    if len(valid_members := self.valid_members(self.get_vc_members(after.channel))) > 1:
                        for m in valid_members:
                            gp = await self.get_guild_profile(m.id, member.guild.id)
                            gp.record_voice_activity()
                            gp.profile.record_voice_activity()
                else:
                    pass

            # if channel hop, close activity
            elif before.channel != after.channel:
                guild_profile.close_voice_activity()
                guild_profile.profile.close_voice_activity()

                # if new channel has enough members, start their xp
                if len(members := self.get_vc_members(after.channel)) > 1:
                    if len(valid_members := self.valid_members(members)) > 1:
                        for m in valid_members:
                            gp = await self.get_guild_profile(m.id, member.guild.id)
                            gp.record_voice_activity()
                            gp.profile.record_voice_activity()

                # if old channel lost enough members, close their xp
                if len(members_remain := self.get_vc_members(before.channel)) < 2:
                    valid_members = self.valid_members(members_remain)
                    for m in valid_members:
                        gp = await self.get_guild_profile(m.id, member.guild.id)
                        gp.close_voice_activity()
                        gp.profile.close_voice_activity()
            else:
                pass

        # user join a channel
        if not before.channel and after.channel:
            # if enough members, start their xp
            if len(members := self.get_vc_members(after.channel)) > 1:
                if len(valid_members := self.valid_members(members)) > 1:
                    for m in valid_members:
                        gp = await self.get_guild_profile(m.id, member.guild.id)
                        gp.record_voice_activity()
                        gp.profile.record_voice_activity()

    @ Cog.listener()
    async def on_ready(self):
        for g in self.bot.guilds:
            for vc in g.voice_channels:
                if len(members := self.get_vc_members(vc)) > 1:
                    if len(valid_members := self.valid_members(members)) > 1:
                        for m in valid_members:
                            gp = await self.get_guild_profile(m.id, m.guild.id)
                            gp.record_voice_activity()
                            gp.profile.record_voice_activity()
