import discord
import datetime



class ModerationAction(object):

    def __init__(self, ctx, action_type, target, reason=None):
        self.ctx = ctx
        self.action_type = action_type
        self.target = target
        self.moderator = self.ctx.author
        self.reason = reason
        self.guild = self.ctx.guild

    @property
    def document(self):
        _ = {
            "action_type": self.action_type.__name__,
            "moderator_id": self.moderator.id,
        }
        try:
            _["target_id"] = self.target.id
        except AttributeError:
            _["target_id"] = self.target
        if self.reason:
            _["reason"] = self.reason
        return _

    async def dispatch(self, title):
        self.ctx.bot.dispatch("moderation", self)
        _ = self.ctx.embed_line(title)
        _.description = f"**Reason:** {self.reason}"
        _.timestamp = datetime.datetime.now()
        try:
            profile = await self.ctx.fetch_member_profile(self.target.id)
        except AttributeError:
            profile = await self.ctx.fetch_member_profile(self.target)
        _id = await self.ctx.bot.discordDB.set(self.document)
        await profile.log_moderation(_id)
        try:
            return await self.target.send(embed=_)
        except (discord.Forbidden, AttributeError):
            pass
