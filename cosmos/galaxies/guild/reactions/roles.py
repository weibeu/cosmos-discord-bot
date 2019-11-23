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

    @Reactions.reaction.command(name="role", aliases=["roles"])
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
        roles = ctx.guild_profile.reactions.get_roles_bullets(roles)
        if not message:
            embed = ctx.embeds.primary()
            embed.set_author(name=message)
            for role, emote in roles:
                embed.description += f"{emote} {role.mention}\n"
            message = await ctx.send(embed=embed)
            for _, emote in roles:
                await message.add_reaction(emote)
        await ctx.guild_profile.reactions.add_roles(message.id, roles)
        await ctx.send_line(f"✅    Provided roles has been set as reaction roles.")
