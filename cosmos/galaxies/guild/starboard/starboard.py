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

    @Settings.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.guild_id:
            return
        if payload.emoji.name not in self.STARS:
            return

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        if [r for r in message.reactions if r.emoji == self.bot.emotes.misc.christmasstar]:
            return  # Ignore when message is already sent to starboard channel. # TODO: Update stars count if possible.

        guild_profile = await self.bot.guild_cache.get_profile(payload.guild_id)
        if starboard := guild_profile.starboard:
            count = len({member for member in itertools.chain.from_iterable([
                await reaction.users().flatten() for reaction in message.reactions])})
            if count == starboard.count:
                embed = guild_profile.theme.get_embed()
                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                embed.description = message.content
                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)
                embed.timestamp = message.created_at
                embed.add_field(name="Original Message", value=f"[Jump!]({message.jump_url})")
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
