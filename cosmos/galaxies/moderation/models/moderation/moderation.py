import discord
import datetime

from cosmos import exceptions


class ModerationAction(object):

    def __init__(self, guild_profile, target, moderator, action_type, reason=None):
        self.guild_profile = guild_profile
        self.bot = self.guild_profile.plugin.bot
        self.target = target
        if self.target.bot:
            raise exceptions.UserIsBotError
        self.moderator = moderator
        self.action_type = action_type
        self.reason = reason or "Reason not specified."

    @property
    def document(self):
        _ = {
            "action_type": self.action_type.__name__,
            "moderator_id": self.moderator.id,
            "reason": self.reason,
        }
        try:
            _["target_id"] = self.target.id
        except AttributeError:
            _["target_id"] = self.target
        return _

    async def dispatch(self, title):
        self.bot.dispatch("moderation", self)
        _ = self.bot.theme.embeds.one_line.primary(title)
        _.description = f"**Reason:** {self.reason}"
        _.timestamp = datetime.datetime.now()
        try:
            profile = await self.guild_profile.fetch_member_profile(self.target.id)
        except AttributeError:
            profile = await self.guild_profile.fetch_member_profile(self.target)
        _id = await self.bot.discordDB.set(self.document)
        await profile.log_moderation(_id)
        try:
            return await self.target.send(embed=_)
        except (discord.Forbidden, AttributeError):
            pass
