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

from .models import GuildEmotes


class CosmosEmotes(object):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.fetch_emotes())

    async def fetch_emotes(self):
        await self.bot.wait_until_ready()
        for guild_name, guild_id in self.bot.configs.emotes.raw.items():
            guild = self.bot.get_guild(guild_id)
            emotes = GuildEmotes(guild.emojis)
            self.__setattr__(guild_name, emotes)
