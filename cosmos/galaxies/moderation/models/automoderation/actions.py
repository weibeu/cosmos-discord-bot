from ..moderation.moderation import ModerationAction

from ..moderation import actions


class AutoModerationActions(object):

    def __init__(self, trigger):
        self._trigger = trigger

    @property
    def embed(self):
        return self._trigger.profile.plugin.bot.theme.embeds.one_line.primary

    @staticmethod
    async def delete(message=None, **_):
        await message.delete()

    async def warn(self, *, message=None, **_):
        if message:
            await message.channel.send(message.author.mention, embed=self.embed(
                    f"⚠    You are being warned for violating {self._trigger.name}."), delete_after=4)
            await ModerationAction(
                self._trigger.profile, message.author, message.guild.me,
                actions.Warned(True), f"For violating {self._trigger.name}").dispatch(
                f"⚠    You were warned in {self._trigger.profile.guild.name}.")

    async def mute(self, *, member, **kwargs):
        pass

    async def kick(self, *, member, **kwargs):
        pass

    async def ban(self, *, member, **kwargs):
        pass
