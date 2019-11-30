from cosmos.core.utilities import converters

import typing
import discord

from discord.ext import commands
from .reactions import Reactions


class ReactionRoles(Reactions):

    INESCAPABLE = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emotes = []

    @Reactions.listener()
    async def on_ready(self):
        # Sort manually. Don't trust discord.
        self.emotes = sorted(self.bot.emotes.foods.emotes, key=lambda emote: emote.created_at)

    async def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            raise commands.MissingPermissions
        return True

    @Reactions.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        guild_profile = await self.bot.guild_cache.get_profile(payload.guild_id)
        if roles := guild_profile.reactions.roles.get(payload.message_id):
            emote = self.bot.get_emoji(payload.emoji.id)
            role = roles[self.emotes.index(emote)]
            member = await guild_profile.guild.fetch_member(payload.user_id)
            await member.add_roles(role, reason="Issued reaction role.")
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            try:
                await message.remove_reaction(emote, member)
            except discord.Forbidden:
                pass

    @Reactions.reaction.group(name="role", aliases=["roles"], invoke_without_command=True)
    async def reaction_roles(self, ctx):
        if not ctx.guild_profile.reactions.roles:
            return await ctx.send_line(f"❌    {ctx.guild.name} has no reactions roles set.", ctx.guild.icon_url)

    @reaction_roles.command(name="add", aliases=["setup", "set"])
    async def add_roles(self, ctx, message: typing.Optional[discord.Message], *, roles: converters.RoleConvertor):
        # Lookup by “{channel ID}-{message ID}” (retrieved by shift-clicking on “Copy ID”).
        # Lookup by message ID (the message must be in the context channel).
        # Lookup by message URL.
        if len(roles) >= self.plugin.data.reactions.max_roles:
            return await ctx.send_line(f"❌    You can't include anymore roles.")
        if not await ctx.confirm():
            return
        roles_emotes = list(zip(roles, self.emotes))
        if not isinstance(message, discord.Message):
            message = message or "Reaction Roles"
            embed = ctx.embeds.primary()
            embed.set_author(name=message)
            embed.description = "\n".join([f"{emote} {role.mention}" for role, emote in roles_emotes])
            message = await ctx.send(embed=embed)
        for _, emote in roles_emotes:
            await message.add_reaction(emote)
        await ctx.guild_profile.reactions.add_roles(message.id, roles)
        await ctx.send_line(f"✅    Provided roles has been set as reaction roles.")
