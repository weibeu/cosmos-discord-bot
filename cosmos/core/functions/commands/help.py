from discord.ext.commands import HelpCommand


class CosmosHelp(HelpCommand):

    COMMUNITY_INVITE = "https://discord.gg/UYAJX3W"

    BASE_URL = "https://cosmos.thecosmos.space/"
    BRAND_ICON = "https://i.imgur.com/0TjctCy.jpg"
    BRAND_LOGO = "https://i.imgur.com/1LFEUdu.png"

    async def send_bot_help(self, mapping):
        embed = self.context.embeds.primary()
        embed.set_thumbnail(url=self.BRAND_ICON)
        embed.set_author(name="Cosmos Discord Bot", icon_url=self.context.bot.user.avatar_url)
        embed.set_footer(text="| The Cosmos", icon_url=self.BRAND_LOGO)
        embed.description = f"Check the [documentation]({self.BASE_URL}) for full reference of all" \
                            f"plugins and commands. Feel free to [join our community](" \
                            f"{self.COMMUNITY_INVITE}) for help with anything."
        arrow = self.context.bot.emotes.misc.next
        embed.add_field(name="Support Us", value=f"{arrow} [Patreon](https://www.patreon.com/__thecosmos)\n"
                                                 f"{arrow} [PayPal](https://paypal.me/thecosmoss/)\n")
        embed.add_field(name="Links", value=f"{arrow} [Invite](https://discordapp.com/oauth2/authorize?"
                                            "client_id=390176338729893889&scope=bot&permissions=8)\n"
                                            # f"- [Home Page]({self.BASE_URL})\n"
                                            f"{arrow} [GitHub](https://github.com/thec0sm0s/cosmos-discord-bot)\n"
                                            # f"- [Community]({self.COMMUNITY_INVITE})\n"
                                            # f"- [Documentation]({self.BASE_URL}galaxy-reference/)\n")
                        )

        destination = self.get_destination()
        await destination.send(embed=embed)
