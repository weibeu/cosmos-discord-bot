import typing
import discord

from .._models.base import GuildBaseCog
from discord.ext.commands import has_permissions, Greedy


class Levels(GuildBaseCog):

    @GuildBaseCog.group(name="level", aliases=["levels"], invoke_without_command=True)
    async def levels(self, ctx, *, member: discord.ext.commands.MemberConverter = None):
        member = member or ctx.author
        profile = await self.bot.profile_cache.get_guild_profile(member.id, ctx.guild.id)
        embed = self.bot.theme.embeds.primary()
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.add_field(name="Level", value=profile.level)
        embed.add_field(name="XP", value=profile.xp)
        await ctx.send(embed=embed)

    @levels.group(name="reward", aliases=["rewards"], invoke_without_command=True)
    async def rewards(self, ctx, level: int):
        _reward = ctx.guild_profile.levels.rewards.get(level)
        if not _reward:
            return await ctx.send_line(f"❌    There are no rewards assigned for level {level}.")
        embed = self.bot.theme.embeds.primary(title=f"Rewards - Level {level}")
        embed.add_field(name="Roles", value=" ".join([f"<@&{role_id}>" for role_id in _reward.roles]))
        if _reward.points:
            embed.add_field(name="Points", value=_reward.points)
        await ctx.send(embed=embed)

    @rewards.command(name="set")
    @has_permissions(administrator=True)
    async def set_rewards(self, ctx, level: int, points: typing.Optional[int] = 0, *, roles: Greedy[discord.Role]):
        embed = self.bot.theme.embeds.primary(title=f"Are you sure to set following rewards for Level {level}?")
        embed.add_field(name="Roles", value=" ".join([role.mention for role in roles]))
        if points:
            embed.add_field(name="Points", value=points)
        if await ctx.confirm(await ctx.send(embed=embed)):
            await ctx.guild_profile.levels.set_rewards(level, [role.id for role in roles], points)
            await ctx.send_line(f"✅    Rewards for Level {level} has been set.")
