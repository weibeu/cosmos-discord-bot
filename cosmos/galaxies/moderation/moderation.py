from .models import ModerationAction, actions
from discord.ext import commands

import discord
import typing

from .. import Cog


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

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def __modlogs_parser(self, ctx, _id, _):
        log = await self.bot.discordDB.get(_id)
        moderator = ctx.guild.get_member(log.moderator_id)
        try:
            reason = log.reason
        except AttributeError:
            reason = "Reason not specified."
        value = f"**Reason:** {reason}\n**Moderator:** {moderator}"
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

    @Cog.group(name="modlogs", invoke_without_command=True)
    @check_mod(kick_members=True)
    async def moderation_logs(self, ctx, *, member: typing.Union[discord.Member, int]):
        try:
            _id = member.id
        except AttributeError:
            _id = member
        profile = await ctx.fetch_member_profile(_id)
        if not profile.moderation_logs:
            return await ctx.send_line(f"❌    {member.name} has no recorded moderation logs.")
        paginator = ctx.get_field_paginator(profile.moderation_logs, entry_parser=self.__modlogs_parser, inline=False)
        paginator.embed.description = f"**User:** `{member}`\n**User ID:** `{_id}`"
        await paginator.paginate()
        # TODO: Add moderation logs limits.
        # TODO: Use discord.User.

    @moderation_logs.command(name="clean", aliases=["purge", "clear"])
    @check_mod(administrator=True)
    async def clean_moderation_logs(self, ctx, *, member: discord.Member):
        if not await ctx.confirm(f"⚠    Are you sure to purge moderation logs of {member}?"):
            return
        profile = await ctx.fetch_member_profile(member.id)
        await profile.clear_moderation_logs()
        await ctx.send_line(f"✅    Moderation logs of {member} has been purged.")

    @Cog.command(name="warn")
    @check_mod(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        if not check_hierarchy(ctx.author, member):
            return await ctx.send_line(f"❌    You can't warn {member}.")
        action = ModerationAction(ctx, actions.Warned, member, reason)
        if await action.dispatch(f"⚠    You were warned in {ctx.guild.name}."):
            res = f"✅    {member} has been warned."
        else:
            res = f"✅    Failed to warn {member}. Warning logged."
        await ctx.send_line(res)

    @Cog.command(name="kick")
    @check_mod(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if not check_hierarchy(ctx.author, member):
            return await ctx.send_line(f"❌    You can't kick {member}.")
        action = ModerationAction(ctx, actions.Kicked, member, reason)
        await action.dispatch(f"👢    You were kicked from {ctx.guild.name}.")
        await member.kick(reason=reason)
        embed = ctx.embed_line(f"✅    {member} has been kicked from the server.")
        await self.__inject_presets(ctx, embed)
        await ctx.send(embed=embed)

    @Cog.command(name="ban")
    @check_mod(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: typing.Union[discord.Member, int], *, reason=None):
        action = ModerationAction(ctx, actions.Banned, member, reason)
        await action.dispatch(f"‼    You were banned from {ctx.guild.name}.")
        try:
            if isinstance(member, discord.Member):
                if not check_hierarchy(ctx.author, member):
                    return await ctx.send_line(f"❌    You can't ban {member}.")
                await member.ban(reason=reason)
            else:
                await ctx.guild.ban(discord.Object(member), reason=reason)
        except discord.HTTPException:
            return await ctx.send_line(f"❌    Failed to ban {member}.")
        embed = ctx.embed_line(f"✅    {member} has been banned from the server.")
        await self.__inject_presets(ctx, embed)
        await ctx.send(embed=embed)

    @Cog.command(name="unban")
    @check_mod(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason=None):
        action = ModerationAction(ctx, actions.Unbanned, user_id, reason)
        try:
            await ctx.guild.unban(discord.Object(user_id), reason=reason)
        except discord.HTTPException:
            return await ctx.send_line(f"❌    Failed to unban {user_id}.")
        await action.dispatch(f"✅    You were unbanned from {ctx.guild.name}.")
        await ctx.send_line(f"✅    {user_id} has been unbanned.")

    @Cog.group(name="mute", invoke_without_command=True)
    @check_voice_perms(mute_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        if not check_hierarchy(ctx.author, member):
            return await ctx.send_line(f"❌    You can't mute {member}.")
        action = ModerationAction(ctx, actions.Muted, member, reason)
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
    @check_voice_perms(mute_members=True)
    async def unmute(self, ctx, member: discord.Member):
        action = ModerationAction(ctx, actions.UnMuted, member)
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
    @commands.has_permissions(administrator=True)
    async def muted_role(self, ctx, *, role: discord.Role = None):
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
