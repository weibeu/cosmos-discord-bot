from cosmos.core.utilities import converters

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
        for message_id, roles in ctx.guild_profile.reactions.roles.items():
            value = "`ROLES:` " + " ".join([role if not role else role.mention for role in roles])
            embed.add_field(name=f"{ctx.emotes.misc.next}    {message_id}", value=value)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @reaction_roles.command(name="add", aliases=["setup", "set"])
    async def add_roles(self, ctx,
                        message: typing.Union[discord.Message, str] = None, *, roles: converters.RoleConvertor):
        """Setup reaction roles over any custom message you wish or you may skip this parameter to let bot post
        a embed displaying list of provided roles.

        To use custom message, you can pass its shareable URL which can be obtained by right clicking over your custom
        message and click `Copy Message Link` from the floating menu. If you're using this command in same channel your
        message is present, you can simply pass its message ID.

        """
        # Lookup by “{channel ID}-{message ID}” (retrieved by shift-clicking on “Copy ID”).
        # Lookup by message ID (the message must be in the context channel).
        # Lookup by message URL.
        # noinspection PyTypeChecker
        if len(roles) >= self.plugin.data.reactions.max_roles:
            return await ctx.send_line(f"❌    You can't include anymore roles.")
        if len(ctx.guild_profile.reactions.roles) >= self.plugin.data.reactions.max_messages:
            return await ctx.send_line(f"❌    You cannot create anymore reaction roles.")
        if not await ctx.confirm():
            return
        # noinspection PyTypeChecker
        roles_emotes = list(zip(roles, self.emotes))
        if not isinstance(message, discord.Message):
            message = message or "Reaction Roles"
            embed = ctx.embeds.primary()
            embed.set_author(name=message)
            embed.description = "```css\nReact to the emote corresponding to the role you wish to have.```\n"
            embed.description += "\n".join([f"{emote} {role.mention}" for role, emote in roles_emotes]) + "\n​"
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            message = await ctx.send(embed=embed)
        for _, emote in roles_emotes:
            await message.add_reaction(emote)
        await ctx.guild_profile.reactions.add_roles(message.id, roles)
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
