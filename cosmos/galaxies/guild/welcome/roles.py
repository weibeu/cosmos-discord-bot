from .base import WelcomeBase

import discord


class WelcomeRoles(WelcomeBase):
    """Assign roles to new members right after they join your server."""

    @WelcomeBase.listener()
    async def on_member_join(self, member):
        guild_profile = await self.cache.get_profile(member.guild.id)
        if guild_profile.welcome_roles:
            await member.add_roles(*guild_profile.welcome_roles, reason="Welcome Roles")

    @WelcomeBase.welcome.group(name="roles", aliases=["role"])
    async def welcome_roles(self, ctx):
        """Displays the list of roles being assigned to every new members joining the server."""

    @welcome_roles.command(name="set", aliases=["setup", "add"])
    async def set_welcome_roles(self, ctx, *roles: discord.Role):
        """Set roles which will be assigned to every new members joining your server."""
        await ctx.guild_profile.set_welcome_roles(roles)
        await ctx.send_line(f"✅    Provided roles has been set for welcome roles.")

    @welcome_roles.command(name="remove", aliases=["delete", "clear"])
    async def remove_welcome_roles(self, ctx):
        """Remove all of the roles from welcome roles if set any."""
        if not await ctx.confirm():
            return
        await ctx.guild_profile.remove_welcome_roles()
        await ctx.send_line(f"✅    All of the roles has been removed from welcome roles.")
