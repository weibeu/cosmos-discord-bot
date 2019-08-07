import discord
import datetime


class ModerationAction(object):

    def __init__(self, bot, target, moderator, action_type, reason=None):
        self.bot = bot
        self.target = target
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
        _id = await self.bot.discordDB.set(self.document)
        await self.target.log_moderation(_id)
        try:
            return await self.target.send(embed=_)
        except (discord.Forbidden, AttributeError):
            pass
