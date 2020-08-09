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
import functools

from ... import Cog


def logger_event(*args, set_title=True, **kwargs):

    def decorator(function):
        @Cog.listener(*args, **kwargs)
        @functools.wraps(function)
        async def wrapper(cog, *_args):
            try:
                if not _args[0].guild:
                    return
                guild_profile = await cog.bot.guild_cache.get_profile(_args[0].guild.id)
            except AttributeError:
                try:
                    guild_profile = _args[0].guild_profile    # Event triggered from ModerationAction.
                except AttributeError:
                    if not isinstance(_args[0], discord.Guild):
                        return
                    guild_profile = await cog.bot.guild_cache.get_profile(_args[0].id)
            if not guild_profile:
                return
            logger = guild_profile.get_logger(function.__name__)
            if not logger:
                return
            embed = cog.embed()
            if set_title:
                embed.title = function.__name__.lstrip("on_").replace("_", " ").title()
            embed.timestamp = datetime.datetime.now()
            response = await function(cog, embed, *_args)
            # TODO: Add auto moderation details on logs.
            if not response:
                return
            try:
                await logger.channel.send(embed=response)
            except AttributeError:
                embed, content = response
                await logger.channel.send(content, embed=embed)
        return wrapper

    return decorator


class LoggerEvents(Cog):

    IGNORED_EVENTS = [
        "on_guild_update",
    ]

    # TODO: Add reactions based actions.

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.loggers = [name for name, _ in self.get_listeners() if name not in self.IGNORED_EVENTS]

    @property
    def embed(self):
        return self.bot.theme.embeds.primary

    @logger_event()
    async def on_message_delete(self, embed, message):
        if message.author.bot:
            return
        if message.clean_content:
            embed.add_field(name="Deleted Message", value=message.clean_content, inline=False)
        embed.add_field(name="Author", value=message.author.mention)
        embed.add_field(name="Author Name", value=message.author)
        embed.add_field(name="Author ID", value=message.author.id)
        embed.add_field(name="From Channel", value=message.channel.mention)
        return embed

    @logger_event()
    async def on_bulk_message_delete(self, embed, messages):
        embed.add_field(name="Messages Deleted", value=f"{len(messages)} messages.")
        if messages:
            embed.add_field(name="From Channel", value=messages[0].channel.mention)
        return embed

    @logger_event()
    async def on_message_edit(self, embed, before, after):
        if after.author.bot:
            return
        embed.add_field(name="Before Edit", value=before.clean_content)
        embed.add_field(name="After Edit", value=after.clean_content)
        embed.add_field(name="Author", value=after.author.mention)
        embed.add_field(name="Author Name", value=after.author)
        embed.add_field(name="Author ID", value=after.author.id)
        embed.add_field(name="In Channel", value=after.channel.mention)
        embed.add_field(name="Actual Message", value=f"[Jump to the message]({after.jump_url})")
        return embed

    @logger_event()
    async def on_guild_channel_pins_update(self, embed, channel, _):
        embed.title = "Message Pinned"
        message = (await channel.pins())[0]
        embed.add_field(name="Message Content", value=message.clean_content, inline=False)
        embed.add_field(name="Author", value=message.author)
        embed.add_field(name="In Channel", value=channel.mention)
        embed.add_field(name="Actual Message", value=f"[Jump to the message]({message.jump_url})")
        return embed

    @logger_event()
    async def on_member_join(self, embed, member):
        embed.add_field(name="Member", value=f"{member.mention}\n{member}")
        embed.add_field(name="Member ID", value=f"`{member.id}`")
        embed.add_field(name="Account Created", value=member.created_at.strftime('%d %B %Y'))
        embed.set_thumbnail(url=member.avatar_url)
        return embed

    @logger_event()
    async def on_member_remove(self, embed, member):
        embed.title = "Member Left"
        embed.color = int("0xF44336", 16)
        embed.add_field(name="Member Name", value=member)
        embed.add_field(name="Member ID", value=f"`{member.id}`")
        embed.set_thumbnail(url=member.avatar_url)
        return embed

    # @logger_event()
    # async def on_member_ban(self, embed, guild, user):
    #     pass
    #
    # @logger_event()
    # async def on_member_unban(self, embed, guild, user):
    #     pass

    @logger_event()
    async def on_moderation(self, embed, action):
        embed.title = str(action.action_type)
        try:
            _id = action.target.id
            embed.add_field(name="Member", value=action.target.mention)
            embed.add_field(name="Member Name", value=action.target)
        except AttributeError:
            _id = action.target
        embed.add_field(name="Member ID", value=f"`{_id}`")
        embed.add_field(name="Reason", value=action.reason)
        embed.add_field(name="Moderator", value=action.moderator.mention)
        return embed

    @logger_event()
    async def on_confession(self, embed, meta):
        embed.set_author(name=meta.identity, url=meta.message.jump_url)
        embed.description = meta.confession
        embed.set_thumbnail(url=meta.user.avatar_url)
        embed.add_field(name="Author", value=f"{meta.user} | {meta.user.mention}")
        embed.set_footer(text=f"ID: {meta.user.id}")
        return embed

    def __get_level_up_embed(self, embed, profile):
        embed.set_author(name=profile.user, icon_url=self.bot.theme.images.chevron)
        embed.set_thumbnail(url=profile.user.avatar_url)
        embed.set_footer(text=profile.guild.name, icon_url=profile.guild.icon_url)
        return embed

    @logger_event()
    async def on_text_level_up(self, embed, profile, _):
        embed = self.__get_level_up_embed(embed, profile)
        embed.description = f"{self.bot.emotes.misc.confetti}    Congratulations {profile.user.name} for " \
                            f"advancing to text **level {profile.level}**."
        return embed, profile.user.mention

    @logger_event()
    async def on_voice_level_up(self, embed, profile):
        embed = self.__get_level_up_embed(embed, profile)
        embed.description = f"{self.bot.emotes.misc.confetti}    Congratulations {profile.user.name} for " \
                            f"advancing to voice **level {profile.voice_level}**."
        return embed, profile.user.mention

    @Cog.listener()
    async def on_guild_update(self, before, after):
        try:
            sub = tuple(set(after.premium_subscribers) - set(before.premium_subscribers))[0]
        except IndexError:
            return
        else:
            self.bot.dispatch("server_boost", sub)

    @logger_event(set_title=False)
    async def on_server_boost(self, embed, sub):
        embed.set_author(name=f"{sub} just boosted the server!", icon_url=self.bot.theme.images.nitro_boost)
        embed.set_thumbnail(url=sub.avatar_url)
        guild_profile = await self.bot.guild_cache.get_profile(sub.guild.id)
        embed.description = guild_profile.presets.get("serverboost", dict()).get("message", str())
        embed.set_footer(text=sub.guild.name, icon_url=sub.guild.icon_url)
        return embed
