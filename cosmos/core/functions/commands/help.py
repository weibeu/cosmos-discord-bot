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

from discord.ext.commands import DefaultHelpCommand

import discord


class CosmosHelp(DefaultHelpCommand):

    async def send_bot_help(self, mapping):

        configs = self.context.bot.configs
        arrow = self.context.bot.emotes.misc.next

        embed = self.context.embeds.primary()
        embed.set_thumbnail(url=configs.info.brand_icon)
        embed.set_author(
            name="Cosmos Discord Bot", icon_url=self.context.bot.user.avatar_url, url=configs.info.homepage)
        embed.set_footer(text="| The Cosmos", icon_url=configs.info.brand_logo)
        embed.description = f"Check the [documentation]({configs.info.homepage}) for full reference of all " \
                            f"plugins and commands. Feel free to [join our community](" \
                            f"{configs.info.community}) for help with anything."
        embed.add_field(name="Support Us", value=f"{arrow} [Patreon]({configs.info.patreon})\n"
                                                 f"{arrow} [PayPal]({configs.info.paypal})\n"
                                                 f"{arrow} [Vote]({configs.info.top_vote_page})\n")
        embed.add_field(name="Links", value=f"{arrow} [Invite]({configs.discord.invite_url})\n"
                                            # f"- [Home Page]({self.BASE_URL})\n"
                                            f"{arrow} [GitHub]({configs.info.github})\n"
                                            f"{arrow} [Reference]({configs.info.homepage}reference)\n"
                                            # f"- [Community]({self.COMMUNITY_INVITE})\n"
                                            # f"- [Documentation]({self.BASE_URL}galaxy-reference/)\n")
                        )

        destination = self.get_destination()
        try:
            await destination.send(embed=embed)
        except discord.Forbidden:
            try:
                await self.context.author.send(embed=embed)
                await self.context.author.send(embed=self.context.embed_line(
                    f"I am forbidden from sending messages in #{destination}.", self.context.bot.theme.images.error))
            except discord.Forbidden:
                pass
