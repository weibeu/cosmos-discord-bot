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

from ...functions import Cog


class CosmosInformation(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.command(name="vote")
    async def vote_cosmos(self, ctx):
        """Love Cosmos? Help others find it by voting Cosmos on top.gg bot page <3."""
        res = "Click here to vote Cosmos on top.gg <3."
        await ctx.send_line(res, icon_url=self.bot.theme.images.heart, author_url=self.bot.configs.info.top_vote_page)

    @Cog.command(name="invite")
    async def invite_cosmos(self, ctx):
        """Invite Cosmos to any of the server you manage."""
        res = "Click here to invite Cosmos Bot to your server."
        await ctx.send_line(res, icon_url=self.bot.theme.images.invite, author_url=self.bot.configs.discord.invite_url)
