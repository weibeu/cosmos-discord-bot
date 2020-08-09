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

from cosmos.core.utilities import converters
from discord.ext import commands
from cosmos import exceptions

import typing
import discord

from .reactions import Reactions


class ReactionRoles(Reactions):
    """Plugin to implement reaction based roles in server."""

    INESCAPABLE = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emotes = []

    @Reactions.listener()
    async def on_ready(self):
        # Sort manually. Don't trust discord.
        self.emotes = sorted(self.bot.emotes.foods.emotes, key=lambda emote: emote.created_at)

    @Reactions.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        guild_profile = await self.bot.guild_cache.get_profile(payload.guild_id)
        if rr := guild_profile.reactions.roles.get(payload.message_id):
            role = None
            message = await (await self.bot.fetch_channel(payload.channel_id)).fetch_message(payload.message_id)
            for _, reaction in zip(rr.roles, message.reactions):
                if payload.emoji == reaction.emoji:
                    role = _
                if isinstance(reaction.emoji, str):
                    if payload.emoji.name == reaction.emoji:
                        role = _
            if not role:
                return
            member = await guild_profile.guild.fetch_member(payload.user_id)

            if not rr.permanent:
                if role in member.roles:
                    await member.remove_roles(role, reason="Removed reaction role.")
                    try:
                        await message.remove_reaction(payload.emoji, member)
                    except discord.Forbidden:
                        pass
                    finally:
                        return
                else:
                    if not rr.stack:
                        try:
                            to_remove = tuple(set(rr.roles) & set(member.roles))[0]
                        except IndexError:
                            pass
                        else:
                            await member.remove_roles(to_remove, reason="Member doesn't wants this role anymore.")
                        finally:
                            await member.add_roles(role, reason="Issued reaction role.")
                        try:
                            await message.remove_reaction(payload.emoji, member)
                        except discord.Forbidden:
                            pass
                        finally:
                            return
            if not rr.stack:
                # Check if member already has any of this reaction roles when stack = False.
                if set(member.roles) & set(rr.roles):
                    return
            await member.add_roles(role, reason="Issued reaction role.")
            try:
                await message.remove_reaction(payload.emoji, member)
            except discord.Forbidden:
                pass

    @Reactions.listener()
    async def on_raw_bulk_message_delete(self, payload):
        guild_profile = await self.cache.get_profile(payload.guild_id)
        if not guild_profile.reactions.roles:
            return
        for message_id in payload.message_ids:
            if message_id in guild_profile.reactions.roles:
                await guild_profile.reactions.remove_roles(message_id)

    @Reactions.listener()
    async def on_raw_message_delete(self, payload):
        guild_profile = await self.cache.get_profile(payload.guild_id)
        if payload.message_id in guild_profile.reactions.roles:
            await guild_profile.reactions.remove_roles(payload.message_id)

    @Reactions.reaction.group(name="role", aliases=["roles"], invoke_without_command=True)
    async def reaction_roles(self, ctx):
        """Manage reaction based roles throughout different channels. Reactions are added to specified messages.
        Members can react to automatically get the desired roles.

        """
        if not ctx.guild_profile.reactions.roles:
            return await ctx.send_line(f"❌    You haven't set any reaction roles yet.")
        embed = ctx.embeds.one_line.primary(f"Reaction Roles", ctx.guild.icon_url)
        embed.description = "```css\nDisplaying all reaction roles attached to messages set in the server with IDs.```"
        for rr in ctx.guild_profile.reactions.roles.values():
            value = " ".join([role if not role else role.mention for role in rr.roles])
            embed.add_field(name=f"{ctx.emotes.misc.next}    {rr.message_id}", value=value, inline=False)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    # noinspection PyTypeChecker
    @reaction_roles.command(name="add", aliases=["setup", "set"])
    @commands.bot_has_permissions(manage_roles=True, add_reactions=True, manage_messages=True, external_emojis=True)
    async def add_roles(
            self, ctx, message: typing.Union[discord.Message, str] = None, stack: typing.Optional[bool] = True,
            permanent: typing.Optional[bool] = False, *, roles: converters.RoleConvertor):
        """Setup reaction roles over any custom message you wish or you may skip this parameter to let bot post
        a embed displaying list of provided roles.

        The stack parameter determines if these roles can be stacked over member or not. Defaults to True or Yes,
        meaning members can have more than one of these roles. Pass 'no' to restrict and let them have only one
        of these roles.

        The permanent parameter determines if these roles once added, can be auto removed by members or not.
        Defaults to False or No. Meaning, members can remove this role anytime by clicking on the corresponding
        reaction if they already have this role. Specify no if you want to refrain them from automatically
        removing it.

        To use custom message, you can pass its shareable URL which can be obtained by right clicking over your custom
        message and click `Copy Message Link` from the floating menu. If you're using this command in same channel your
        message is present, you can simply pass its message ID.

        """
        # Lookup by “{channel ID}-{message ID}” (retrieved by shift-clicking on “Copy ID”).
        # Lookup by message ID (the message must be in the context channel).
        # Lookup by message URL.
        if len(roles) >= self.plugin.data.reactions.max_roles:
            return await ctx.send_line(f"❌    You can't include anymore roles.")
        if len(ctx.guild_profile.reactions.roles
               ) >= self.plugin.data.reactions.max_messages and not ctx.guild_profile.is_prime:
            raise exceptions.GuildNotPrime("Click to get prime to create more reaction roles with all other features.")
        if not await ctx.confirm():
            return
        roles_emotes = list(zip(roles, self.emotes))
        if not isinstance(message, discord.Message):
            message = message or "Reaction Roles"
            embed = ctx.embeds.primary()
            embed.set_author(name=message, icon_url=self.bot.theme.images.diabetes)
            # embed.description = "```css\nReact to the emote corresponding to the role you wish to have.```\n"
            for role, emote in roles_emotes:
                embed.add_field(name=f"{emote}    {role.name}", value=f"`COLOR:` {role.mention}")
            # embed.description += "\n".join([f"{emote} {role.mention}" for role, emote in roles_emotes]) + "\n​"
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            message = await ctx.send(embed=embed)
        if len(message.reactions) < len(roles):
            try:
                await message.clear_reactions()
            except discord.Forbidden:
                return await ctx.send_line(
                    f"❌    The reactions on messages is less than roles you want to use.")
            else:
                for _, emote in roles_emotes:
                    await message.add_reaction(emote)
        else:
            for _, reaction in zip(roles, message.reactions):
                await message.add_reaction(reaction.emoji)
        await ctx.guild_profile.reactions.add_roles(message.id, roles, stack, permanent)
        await ctx.send_line(f"✅    Provided roles has been set as reaction roles.")

    @reaction_roles.command(name="remove", aliases=["delete"])
    async def remove_roles(self, ctx, message: typing.Union[discord.Message, int]):
        """Remove reaction roles from provided message.

        To use custom message, you can pass its shareable URL which can be obtained by right clicking over your custom
        message and click `Copy Message Link` from the floating menu. If you're using this command in same channel your
        message is present, you can simply pass its message ID.

        """
        if not ctx.guild_profile.reactions.roles:
            return await ctx.send_line(f"❌    {ctx.guild.name} has no reactions roles set.", ctx.guild.icon_url)
        message_id = message.id if isinstance(message, discord.Message) else message
        if message_id not in ctx.guild_profile.reactions.roles:
            return await ctx.send_line("❌    That message doesn't contains any reaction roles.")
        if not await ctx.confirm():
            return
        await ctx.guild_profile.reactions.remove_roles(message_id)
        await ctx.send_line(f"✅    Reaction roles has been removed for provided message.")

    @reaction_roles.command(name="clean", aliases=["clear"])
    async def clean_roles(self, ctx):
        """Removes all of the reaction roles which has been set in the server."""
        if not ctx.guild_profile.reactions.roles:
            return await ctx.send_line(f"❌    {ctx.guild.name} has no reactions roles set.", ctx.guild.icon_url)
        if not await ctx.confirm():
            return
        await ctx.guild_profile.reactions.remove_all_reaction_roles()
        await ctx.send_line(f"✅    All of the reaction roles has been cleared and removed.")
