from cosmos.core.utilities import converters

import typing
import discord

from discord.ext import commands
from .reactions import Reactions


class ReactionRoles(Reactions):

    INESCAPABLE = False

    async def cog_check(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            raise commands.MissingPermissions
        return True

    @Reactions.reaction.group(name="role", aliases=["roles"])
    async def reaction_roles(self, ctx):
        pass

    @reaction_roles.command(name="add", aliases=["setup", "set"])
    async def add_roles(self, ctx, message: typing.Optional[discord.Message], *, roles: converters.RoleConvertor):
        # Lookup by “{channel ID}-{message ID}” (retrieved by shift-clicking on “Copy ID”).
        # Lookup by message ID (the message must be in the context channel).
        # Lookup by message URL.
        if len(roles) >= self.plugin.data.reactions.max_roles:
            return await ctx.send_line(f"❌    You can't include more than twenty roles.")
        if not await ctx.confirm():
            return
        roles_emotes = list(zip(roles, self.bot.emotes.foods.emotes))
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
