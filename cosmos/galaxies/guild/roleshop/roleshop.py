import discord

from .settings import RoleShopSettings


class RoleShop(RoleShopSettings):

    @RoleShopSettings.listener()
    async def on_message(self, message):
        profile = await self.bot.profile_cache.get_guild_profile(message.author.id, message.guild.id)
        if profile and not profile.in_points_buffer:
            self.bot.loop.create_task(profile.give_default_points())

    @RoleShopSettings.group(invoke_without_command=True)
    async def points(self, ctx, member: discord.Member = None):
        if member:
            adverb = f"{member.name} has"
        else:
            member = ctx.author
            adverb = f"{member.name}, you have"
        if member.bot:
            return await ctx.send_line("🤖    Robos don't earn points.")

        profile = await self.bot.profile_cache.get_guild_profile(member.id, ctx.guild.id)
        await ctx.send_line(f"💰    {adverb} {profile.points} guild points.")
