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

from ..settings.base import Settings

import discord
import itertools


class Starboard(Settings):
    """A plugin which implements Starboard feature in server.

    Reactions on messages when exceed specified number of stars, they are posted in a certain channel which has been
    set previously.

    """

    INESCAPABLE = False

    STARS = [
        "⭐", "🌟", "🤩",
    ]

    # TODO: Remove the post from starboard if count < starboard.count.

    @Settings.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.guild_id:
            return
        if payload.emoji.name not in self.STARS:
            return

        user = self.bot.get_user(payload.user_id)
        if not user or user.bot:
            return

        guild_profile = await self.bot.guild_cache.get_profile(payload.guild_id)
        if starboard := guild_profile.starboard:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            count = len({member for member in itertools.chain.from_iterable([
                await reaction.users().flatten() for reaction in message.reactions if reaction.emoji in self.STARS])})

            if [r for r in message.reactions if r.emoji == self.bot.emotes.misc.christmasstar]:
                # Message is already sent to starboard channel. # TODO: Implement caching.
                # Find the starboard message of this message.
                async for m in starboard.channel.history():
                    try:
                        e = m.embeds[0]
                    except IndexError:
                        continue
                    try:
                        _id = int(e.footer.text)
                    except (ValueError, TypeError):
                        continue
                    if not _id == message.id:
                        continue
                    # Attempt to update Stars Meta.
                    e.remove_field(-1)
                    e.add_field(name="Stars Meta", value=f"⭐ **{count}**")    # Update the stars count.
                    return await m.edit(embed=e)

            if count == starboard.count:
                embed = guild_profile.theme.get_embed()
                embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                try:
                    embed_ = message.embeds[0]
                except IndexError:
                    embed_ = None
                if message.content:
                    description = message.content
                else:
                    description = embed_.description if (embed_ and embed_.description) else str()
                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)
                else:
                    try:
                        embed.set_image(url=embed_.image.url)
                    except (AttributeError, TypeError):
                        pass
                embed.timestamp = message.created_at
                embed.description = f"{self.bot.emotes.misc.next}    {description}" if description else str()
                embed.add_field(name="Original Message", value=f"[Jump!]({message.jump_url})")
                embed.add_field(name="Channel", value=message.channel.mention)
                embed.add_field(name="Stars Meta", value=f"⭐ **{count}**")
                embed.set_footer(text=message.id, icon_url=guild_profile.guild.icon_url)
                await starboard.channel.send(embed=embed)
                # Set flag to mark that message has been posted to starboard channel.
                await message.add_reaction(self.bot.emotes.misc.christmasstar)

    @Settings.group(name="starboard")
    async def starboard(self, ctx):
        """Configure Starboard in server."""
        pass

    @starboard.command(name="set", aliases=["setup", "create"])
    async def set_starboard(self, ctx, stars: int = None, *, channel: discord.TextChannel = None):
        """Set starboard in server for specified number of stars in specified channel."""
        stars = stars or self.plugin.data.settings.default_star_count
        channel = channel or ctx.channel
        if not channel.permissions_for(ctx.me).send_messages:
            return await ctx.send_line(f"❌    Please permit me to send messages in {channel} first.")
        if not await ctx.confirm():
            return
        await ctx.guild_profile.set_starboard(channel, stars)
        await ctx.send_line(f"Starboard has been enabled in #{channel}.", ctx.guild.icon_url)

    @starboard.command(name="remove", aliases=["delete"])
    async def remove_starboard(self, ctx):
        """Remove starboard from server."""
        if not await ctx.confirm():
            return
        await ctx.guild_profile.remove_starboard()
        await ctx.send_line("Starboard has been removed.", ctx.guild.icon_url)
