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

from .models import ModerationAction, actions
from discord.ext import commands

import discord
import typing

from .. import Cog


class FakeGuildMember(discord.Object):

    bot = False

    def __str__(self):
        return str(self.id)

    @property
    def name(self):
        return self.__str__()

    @property
    def avatar_url(self):
        return str()


async def _has_permissions(ctx, perms):
    ch = ctx.channel
    permissions = ch.permissions_for(ctx.author)

    if [perm for perm, value in perms.items() if getattr(permissions, perm, None) != value]:
        return False

    return True


async def _moderators_check(ctx):
    guild_profile = await ctx.fetch_guild_profile()
    if not set([role.id for role in ctx.author.roles]) & set(guild_profile.moderators):
        if ctx.author.id not in guild_profile.moderators:
            raise commands.CheckFailure
    return True


def check_mod(**perms):

    async def predicate(ctx):
        if not await _has_permissions(ctx, perms) and not await _moderators_check(ctx):
            raise commands.CheckFailure
        return True

    return commands.check(predicate)


def check_voice_perms(**perms):

    async def predicate(ctx):
        permissions = ctx.author.guild_permissions

        if [perm for perm, value in perms.items() if getattr(permissions, perm, None) != value]:
            if not await _moderators_check(ctx):
                raise commands.CheckFailure
        return True

    return commands.check(predicate)


def check_hierarchy(moderator, target):
    return (moderator.top_role > target.top_role) or moderator.guild.owner == moderator


class _GuildMemberProfile(commands.Converter):

    # TODO: Implement similar global convertors returning custom profiles.

    async def convert(self, ctx, argument):
        member = await commands.MemberConverter().convert(ctx, argument)
        profile = await ctx.fetch_member_profile(member.id)
        if not profile:
            raise commands.BadArgument
        return profile


class Moderation(Cog):
    """Plugin for server moderation."""

    INESCAPABLE = False

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def __modlogs_parser(self, ctx, _id, _):
        log = await self.bot.discordDB.get(_id)
        moderator = ctx.guild.get_member(log.moderator_id)
        if not moderator:
            moderator = await self.bot.fetch_user(log.moderator_id)
        try:
            reason = log.reason
        except AttributeError:
            reason = "Reason not specified."
        value = f"**Reason:** {reason}\n**Moderator:** {moderator.mention}\n" \
                f"**Timestamp:** {log.created_at.strftime('%I:%M %p | %e %B, %Y')}"
        return log.action_type, value

    @staticmethod
    async def __inject_presets(ctx, embed):
        guild_profile = await ctx.fetch_guild_profile()
        presets = guild_profile.presets.get(ctx.command.name, dict())
        if not presets:
            return embed
        image_url = presets["image_url"]
        text = presets.get("text")
        reason = ctx.kwargs.get("reason")
        if image_url:
            embed.set_image(url=image_url)
        if text:
            if reason:
                embed.description = f"**Reason:** {reason} **|** {text}"
            else:
                embed.description = text
        return embed

    @staticmethod
    async def __get_action(ctx, target, action_type, *args, **kwargs):
        return ModerationAction(
            await ctx.fetch_guild_profile(), target, ctx.author, action_type, *args, **kwargs)

    @Cog.group(name="modlogs", invoke_without_command=True, inescapable=False)
    @check_mod(kick_members=True)
    async def moderation_logs(self, ctx, *, member: typing.Union[discord.Member, int]):
        """Displays all of the moderation logs of specified member.

        All of the Timestamps are displayed in UTC.

        """
        member = member if isinstance(member, discord.Member) else FakeGuildMember(member)
        profile = await ctx.fetch_member_profile(member.id)
        if not profile.moderation_logs:
            return await ctx.send_line(f"❌    {member.name} has no recorded moderation logs.")
        paginator = ctx.get_field_paginator(
            profile.moderation_logs, entry_parser=self.__modlogs_parser, inline=False, per_page=7)
        paginator.embed.description = f"**User:** `{member}`\n**User ID:** `{member.id}`"
        paginator.embed.set_author(name="Moderation Logs", icon_url=member.avatar_url)
        await paginator.paginate()
        # TODO: Add moderation logs limits.
        # TODO: Use discord.User.

    @moderation_logs.command(name="clean", aliases=["purge", "clear"])
    @check_mod(administrator=True)
    async def clean_moderation_logs(self, ctx, *, member: discord.Member):
        """Removes and cleans all of the previous moderation logs of specified member."""
        if not await ctx.confirm(f"⚠    Are you sure to purge moderation logs of {member}?"):
            return
        profile = await ctx.fetch_member_profile(member.id)
        await profile.clear_moderation_logs()
        await ctx.send_line(f"✅    Moderation logs of {member} has been purged.")

    @Cog.command(name="warn", inescapable=False)
    @check_mod(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        """Issues a warning to specified member. Also notifies them automatically by direct message."""
        if not check_hierarchy(ctx.author, member):
            return await ctx.send_line(f"❌    You can't warn {member}.")
        action = await self.__get_action(ctx, member, actions.Warned, reason)
        if await action.dispatch(f"⚠    You were warned in {ctx.guild.name}."):
            res = f"✅    {member} has been warned."
        else:
            res = f"✅    Failed to warn {member}. Warning logged."
        await ctx.send_line(res)

    @Cog.command(name="kick", inescapable=False)
    @check_mod(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks specified member from the server. It also notifies them automatically along with the given reason."""
        if not check_hierarchy(ctx.author, member):
            return await ctx.send_line(f"❌    You can't kick {member}.")
        action = await self.__get_action(ctx, member, actions.Kicked, reason)
        await member.kick(reason=reason)
        await action.dispatch(f"👢    You were kicked from {ctx.guild.name}.")
        embed = ctx.embed_line(f"✅    {member} has been kicked from the server.")
        await self.__inject_presets(ctx, embed)
        await ctx.send(embed=embed)

    @Cog.command(name="ban", inescapable=False)
    @check_mod(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: typing.Union[discord.Member, int], *, reason=None):
        """Bans specified member from the server. It also notifies them automatically along with the given reason.
        If the user is not present in the server, their discord ID can be passed as member parameter.

        """
        if isinstance(member, discord.Member):
            if not check_hierarchy(ctx.author, member):
                return await ctx.send_line(f"❌    You can't ban {member}.")
            await member.ban(reason=reason)
        else:
            member = FakeGuildMember(member)
            await ctx.guild.ban(member, reason=reason)
        action = await self.__get_action(ctx, member, actions.Banned, reason)
        await action.dispatch(f"‼    You were banned from {ctx.guild.name}.")
        embed = ctx.embed_line(f"✅    {member} has been banned from the server.")
        await self.__inject_presets(ctx, embed)
        await ctx.send(embed=embed)

    @Cog.command(name="unban", inescapable=False)
    @check_mod(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason=None):
        """Un bans user from their discord ID."""
        user = FakeGuildMember(user_id)
        action = await self.__get_action(ctx, user, actions.Unbanned, reason)
        try:
            await ctx.guild.unban(user, reason=reason)
        except discord.HTTPException:
            return await ctx.send_line(f"Failed to unban user {user_id}.", self.bot.theme.images.error)
        await action.dispatch(f"✅    You were unbanned from {ctx.guild.name}.")
        await ctx.send_line(f"✅    {user_id} has been unbanned.")

    @Cog.command(name="clean", inescapable=False)
    @check_mod(kick_members=True)
    async def clean(self, ctx):
        """Cleans and deleted last few messages sent by the bot."""
        count = 0
        delete_max = 5
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        async for message in ctx.channel.history(limit=30):
            delete = False
            if count > delete_max:
                return

            if message.author.id == self.bot.user.id:
                delete = True

            context = await self.bot.get_context(message)
            if context.valid:
                delete = True

            if delete:
                await message.delete()
                count += 1

    @Cog.group(name="mute", invoke_without_command=True, inescapable=False)
    @commands.bot_has_permissions(manage_roles=True)
    @check_voice_perms(mute_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        """Mutes specified member from voice and also adds the muted role. It also notifies them automatically along
        with the given reason.

        """
        if not check_hierarchy(ctx.author, member):
            return await ctx.send_line(f"❌    You can't mute {member}.")
        action = await self.__get_action(ctx, member, actions.Muted, reason)
        guild_profile = await ctx.fetch_guild_profile()
        muted_role = ctx.guild.get_role(guild_profile.roles.get("muted"))
        if not muted_role:
            return await ctx.send_line(f"❌    Muted role has not been set yet.")
        try:
            await member.edit(mute=True, reason=reason)
        except discord.HTTPException:
            pass    # TODO: Maybe mute them later whenever they join voice channel.
        finally:
            await member.add_roles(muted_role, reason=reason)
        await action.dispatch(f"🤐    You were muted in {ctx.guild.name}.")
        await ctx.send_line(f"✅    {member} has been muted.")
        # TODO: Add an optional time duration.
        # TODO: Keep track of member leaving and joining back guild.

    @Cog.command(name="unmute")
    @commands.bot_has_permissions(manage_roles=True)
    @check_voice_perms(mute_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """Un mutes specified member from voice and removes the muted role. It also notifies them automatically."""
        action = await self.__get_action(ctx, member, actions.Warned)
        guild_profile = await ctx.fetch_guild_profile()
        muted_role = ctx.guild.get_role(guild_profile.roles.get("muted"))
        if not muted_role:
            return await ctx.send_line(f"❌    Muted role has not been set yet.")
        if muted_role not in member.roles:
            return await ctx.send_line(f"❌    {member} is not muted yet.")
        try:
            await member.edit(mute=False)
        except discord.HTTPException:
            pass
        finally:
            await member.remove_roles(muted_role)
        await action.dispatch(f"✅    You have been unmuted in {ctx.guild.name}.")
        await ctx.send_line(f"✅    {member} has been unmuted.")

    @mute.command(name="role")
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def muted_role(self, ctx, *, role: discord.Role = None):
        """Sets muted role for server which will be used to enforce restrictions on members when they're muted.
        It creates a new role to use denying sending messages to all of the text channels if not provided.

        """
        if not await ctx.confirm():
            return
        guild_profile = await ctx.fetch_guild_profile()
        if not role:
            role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(role, send_messages=False)
        await guild_profile.set_role("muted", role.id)
        await ctx.send_line(f"✅    {role.name} has been assigned to be used as muted role.")
        # TODO: Set overrides if new channel has been created.

    async def cog_command_error(self, ctx, error):
        try:
            if isinstance(error.original, discord.Forbidden):
                return await ctx.send_line(
                    f"Cosmos is forbidden to {ctx.command.name} them. Maybe check roles hierarchy?",
                    self.bot.theme.images.no_entry)
        except AttributeError:
            pass

    @Cog.group(name="purge", aliases=["prune"], invoke_without_command=True)
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def purge(self, ctx, search=100):
        """Removes and purges messages which meets specified criteria. To specify any criteria, consider using
        its sub-commands. If this primary command is used, performs the default purge which removes last
        specified number of messages.

        """
        await self.do_removal(ctx, search, lambda m: True)

    @staticmethod
    async def do_removal(ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send_line(f"❌    Too many messages specified to search for.")

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
            await ctx.message.delete()
        except discord.Forbidden:
            return await ctx.send_line("❌    I do not have permissions to delete messages.")

        await ctx.send_line(f"✅    Successfully purged {len(deleted)} messages.", delete_after=5)

    @purge.command(name="text", aliases=["texts"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def text(self, ctx, search=100):
        """Removes all of the messages containing only texts, ignores files or any attachments."""
        await self.do_removal(ctx, search, lambda e: not e.attachments)

    @purge.command(name="embeds", aliases=["embed"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them. Embed messages are sent by webhooks and other bots."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @purge.command(name="files", aliases=["file"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @purge.command(name="images", aliases=["image"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @purge.command(name="all", aliases=["everything"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def _remove_all(self, ctx, search=100):
        """Another alias to the primary purge command which deletes any of the messages for provided search limit."""
        await self.do_removal(ctx, search, lambda e: True)

    @purge.command(name="user", aliases=["member"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages sent by the specified member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @purge.command(name="contains", aliases=["has"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring. The substring must be at least 3 characters long."""
        if len(substr) < 3:
            await ctx.send_line("❌    The substring length must be at least of 3 characters.")
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @purge.command(name="bot")
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @purge.command(name="emoji", aliases=["emojis", "emotes", "emote"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        await self.do_removal(ctx, search, lambda m: self.bot.utilities.count_emojis(m.content))

    @purge.command(name="reactions", aliases=["reaction"])
    @commands.bot_has_permissions(manage_messages=True)
    @check_mod(manage_messages=True)
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send_line(f"❌    Too many messages specified to search for.")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send_line(f"❌    Successfully removed {total_reactions} reactions.")
