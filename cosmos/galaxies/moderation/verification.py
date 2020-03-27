from discord.ext import commands
from typing import Optional

import discord

from .. import Cog


class UserVerification(Cog):
    """Lets users verify themselves before they can join your server. You can implement several verification methods."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def cog_before_invoke(self, ctx):
        ctx.guild_profile = await ctx.fetch_guild_profile()

    async def cog_check(self, ctx):
        await super().cog_check(ctx)
        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])
        return True

    @Cog.listener()
    async def on_member_join(self, member):
        guild_profile = await self.bot.guild_cache.get_profile(member.guild.id)
        if guild_profile.verification.role:
            await member.add_roles(guild_profile.verification.role)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_profile = await self.bot.guild_cache.get_profile(payload.guild_id)
        if not guild_profile.verification.role:
            return
        if guild_profile.verification.reaction_message_id == payload.message_id:
            await payload.member.remove_roles(guild_profile.verification.role)

            self.bot.dispatch("member_verification", guild_profile, payload.member)

    @Cog.group(name="verification", aliases=["verify"], invoke_without_command=True)
    async def verification(self, ctx):
        """Primary command to setup several verification methods."""

    @verification.group(name="role", invoke_without_command=True)
    async def verification_role(self, ctx, *, role: discord.Role):
        """Set the role which will be assigned to unverified members to keep them locked away from accessing normal
        channels and let them go through the verification process.

        """
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, read_messages=False)
        await ctx.guild_profile.verification.set_role(role)
        await ctx.send_line(f"✅    {role.name} has been assigned as verification role.")

    @verification_role.command(name="remove", aliases=["delete"])
    async def remove_verification_role(self, ctx):
        """Removes the verification role hence disabling all of the verification methods from the server."""
        await ctx.guild_profile.verification.remove_role()
        await ctx.send_line(f"✅    Verification role has been removed and methods are disabled.")

    @verification.group(name="reaction", aliases=["react"])
    async def reaction_verification(self, ctx):
        """Primary command for reaction verification method."""
        pass

    @reaction_verification.command(name="set", aliases=["setup"])
    async def set_reaction_verification(self, ctx, message: Optional[discord.Message] = None,
                                        channel: Optional[discord.TextChannel] = None,
                                        emote: Optional[discord.Emoji] = None, icon_url: Optional[str] = None,
                                        image_url: Optional[str] = None, *, description=""):
        """Set react to verify method to authenticate users to your server.
        You can specify the message ID or message URL if you want this reaction to be added over a custom message
        otherwise the default embed is used for the same. The emote you want to use for reacting, custom URLs for
        icon and image and description text or default values will be used.

        """
        if not ctx.guild_profile.verification.role:
            return await ctx.send_line(f"❌    Please set the verification role before using verification methods.")
        emote = emote or "🔓"
        if not message:
            channel = channel or ctx.channel
            embed = ctx.embed_line("Verification", self.bot.theme.images.verified)
            embed.description = description
            if icon_url:
                embed.set_thumbnail(url=icon_url)
            if image_url:
                embed.set_image(url=image_url)
            embed.set_footer(text="Click or tap to the reaction below to verify yourself.", icon_url=ctx.guild.icon_url)
            message = await channel.send(embed=embed)
        await message.add_reaction(emote)
        # Ensure verification role has perms to see this channel.
        await message.channel.set_permissions(ctx.guild_profile.verification.role,
                                              read_messages=True, send_messages=False)
        await message.channel.set_permissions(ctx.guild.default_role, read_messages=False)
        await ctx.guild_profile.verification.set_reaction_verification(message.id)
        await ctx.send_line(f"✅    Reaction verification has been set in the server.")

    @reaction_verification.command(name="remove", aliases=["delete"])
    async def remove_reaction_verification(self, ctx):
        """Removes the reaction verification method from the server."""
        if not await ctx.confirm():
            return
        await ctx.guild_profile.verification.remove_reaction_verification()
        await ctx.send_line(f"✅    Reaction verification method has been removed from the server.")
