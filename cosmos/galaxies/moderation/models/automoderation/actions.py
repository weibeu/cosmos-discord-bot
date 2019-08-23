import asyncio

import discord

from ..moderation.moderation import ModerationAction

from ..moderation import actions


class AutoModerationActions(object):

    def __init__(self, trigger):
        self._trigger = trigger

    @property
    def embed(self):
        return self._trigger.profile.plugin.bot.theme.embeds.one_line.primary

    @property
    def _reason(self):
        return f"For violating {self._trigger.name}."

    @staticmethod
    async def delete(message=None, **_):
        await message.delete()

    async def warn(self, *, message=None, **_):
        if message:
            await message.channel.send(message.author.mention, embed=self.embed(
                    f"⚠    You are being warned for violating {self._trigger.name}."), delete_after=4)
            await ModerationAction(
                self._trigger.profile, message.author, message.guild.me,
                actions.Warned(True), self._reason).dispatch(
                f"⚠    You were auto warned in {self._trigger.profile.guild.name}.")

    async def mute(self, *, member, **_):
        muted_role = self._trigger.profile.guild.get_role(self._trigger.profile.roles.get("muted"))
        try:
            await member.edit(mute=True, reason=self._reason)
        except discord.HTTPException:
            pass  # TODO: Maybe mute them later whenever they join voice channel.
        try:
            await member.add_roles(muted_role, reason=self._reason)
        except AttributeError:
            pass
        await ModerationAction(
            self._trigger.profile, member, member.guild.me, actions.Muted(True), self._reason
        ).dispatch(f"⚠    You were auto muted in {self._trigger.profile.guild.name}")
        await asyncio.sleep(600)
        try:
            await member.edit(mute=False, reason="[Auto] Unmute")
        except discord.HTTPException:
            pass    # TODO: Maybe mute them later whenever they join voice channel.
        try:
            await member.remove_roles(muted_role, reason="[Auto] Unmute")
        except AttributeError:
            pass

    async def kick(self, *, member, **_):
        await member.kick(reason=self._reason)
        await ModerationAction(
            self._trigger.profile, member, member.guild.me, actions.Kicked(True), self._reason
        ).dispatch(f"⚠    You were auto muted from {self._trigger.profile.guild.name}")

    async def ban(self, *, member, **_):
        await ModerationAction(
            self._trigger.profile, member, member.guild.me, actions.Banned(True), self._reason
        ).dispatch(f"⚠    You were auto banned from {self._trigger.profile.guild.name}")
