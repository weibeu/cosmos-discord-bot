import typing
import discord

from discord.ext import commands
from cosmos.core import utilities
from .._models.base import GuildBaseCog


class ChannelConverter(commands.Converter):

    CHANNELS = [
        "text",
        "voice"
    ]

    async def convert(self, ctx, argument):
        if argument.lower() not in self.CHANNELS:
            raise commands.BadArgument
        return argument


class Levels(GuildBaseCog):
    """A plugin to implement text or voice levelling feature in server and related commands."""

    INESCAPABLE = False    # TODO: Fix. It still shows True at runtime.

    @GuildBaseCog.cooldown(1, 5, GuildBaseCog.bucket_type.member)
    @GuildBaseCog.group(name="level", aliases=["levels"], invoke_without_command=True, inescapable=False)
    async def levels(self, ctx, *, member: discord.ext.commands.MemberConverter = None):
        """Displays current level and experience points."""
        member = member or ctx.author
        profile = await self.bot.profile_cache.get_guild_profile(member.id, ctx.guild.id)
        embed = self.bot.theme.embeds.primary()
        embed.set_author(name=member.display_name + "'s Level and XP statistics", icon_url=member.avatar_url)
        text_level_value = f"`LEVEL` **{profile.level}**" \
                           f"\n`XP` **{profile.xp_progress[0]} / {profile.xp_progress[1]}**" \
                           f"\n`TOTAL XP` **{profile.xp}**" \
                           f"\n{utilities.StaticProgressBar(profile.xp_progress[0], profile.xp_progress[1])}"
        voice_level_value = f"`LEVEL` **{profile.voice_level}**" \
                            f"\n`XP` **{profile.voice_xp_progress[0]} / {profile.voice_xp_progress[1]}**" \
                            f"\n`TOTAL XP` **{profile.voice_xp}**\n" \
                            f"{utilities.StaticProgressBar(profile.voice_xp_progress[0], profile.voice_xp_progress[1])}"
        embed.add_field(name="⌨    Text Level", value=text_level_value, inline=False)
        embed.add_field(name="🎤    Voice Level", value=voice_level_value, inline=False)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @staticmethod
    async def __rewards_parser(_, entry, __):    # reward, rewards
        value = str()
        if entry.points:
            value += f"`Points:` **{entry.points}**\n"
        value += f"`Roles:` " + " ".join([f"<@&{_}>" for _ in entry.roles])
        return f"Level {entry.level}", value

    @levels.group(name="reward", aliases=["rewards"], invoke_without_command=True)
    async def rewards(self, ctx, channel: typing.Optional[ChannelConverter] = "text", level: int = None):
        """Displays any rewards set for specified or all of the levels.
        Optionally pass `text` to view Text Levels rewards and `voice` for Voice Levels rewards.

        """
        rewards = ctx.guild_profile.levels.get_rewards(channel)
        if not rewards:
            return await ctx.send_line(f"❌    There are no {channel.title()} Level Rewards set in this server yet.")
        description = "```css\nDisplaying Levels and its rewards which are awarded to members achieving this level.```"
        if not level:
            paginator = ctx.get_field_paginator(
                sorted(
                    rewards.values(), key=lambda reward: reward.level
                ), show_author=False, entry_parser=self.__rewards_parser)
            paginator.embed.description = description
            paginator.embed.set_author(name=f"Level {channel} Rewards".title(), icon_url=ctx.guild.icon_url)
            return await paginator.paginate()
        _reward = rewards.get(level)
        if not _reward:
            return await ctx.send_line(f"❌    There are no {channel.title()} rewards assigned for level {level}.")
        embed = self.bot.theme.embeds.primary()
        embed.description = description
        embed.set_author(name=f"Rewards for {channel.title()} Level {level}", icon_url=ctx.guild.icon_url)
        embed.add_field(name="Roles", value=" ".join([f"<@&{role_id}>" for role_id in _reward.roles]))
        embed.add_field(name="Points", value=_reward.points)
        await ctx.send(embed=embed)

    @rewards.command(name="set")
    @commands.has_permissions(administrator=True)
    async def set_rewards(self, ctx, level: int, channel: typing.Optional[ChannelConverter] = "text",
                          points: typing.Optional[int] = 0, *, roles: utilities.converters.RoleConvertor()):
        """Set rewards for specified Text or Voice Levels.
        You can set one or multiple roles and optionally Guild Points as rewards.

        """
        embed = self.bot.theme.embeds.primary()
        embed.set_author(name=f"Are you sure to set following rewards for "
                              f"{channel.title()} Level {level}?", icon_url=ctx.guild.icon_url)
        embed.add_field(name="Roles", value=" ".join([role.mention for role in roles]))
        embed.add_field(name="Points", value=points)
        if await ctx.confirm(await ctx.send(embed=embed)):
            await ctx.guild_profile.levels.set_rewards(level, [role.id for role in roles], points, channel=channel)
            await ctx.send_line(f"✅    Rewards for {channel.title()} Level {level} has been set.")

    @rewards.command(name="remove", aliases=["delete"])
    @commands.has_permissions(administrator=True)
    async def remove_rewards(self, ctx, level: int, channel: ChannelConverter = "text"):
        """Remove any Text or Voice Level rewards set for specified level."""
        if not ctx.guild_profile.levels.get_rewards(channel).get(level):
            return await ctx.send_line(f"❌    There are no rewards assigned for level {level}.")
        if not await ctx.confirm():
            return
        await ctx.guild_profile.levels.remove_rewards(level, channel=channel)
        await ctx.send_line(f"✅    Rewards for Level {level} has been removed.")
