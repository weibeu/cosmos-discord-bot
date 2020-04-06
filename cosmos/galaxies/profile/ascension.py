from .. import Cog


class _Levels(Cog):
    """This plugin implements experience points and levelling features."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    def __is_ignored(self, message):
        if message.author.id == self.bot.user.id:
            return True
        if message.author.bot:
            return True
        if not message.guild:
            return True

    @Cog.listener()
    async def on_message(self, message):
        if self.__is_ignored(message):
            return

        await self.cache.give_assets(message)

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or after.afk:
            return

        profile = await self.cache.get_profile(member.id)
        if not profile:
            profile = await self.cache.create_profile(member.id)
        guild_profile = await profile.get_guild_profile(member.guild.id)

        if ((before.mute and not after.mute)
                or (before.self_mute and not after.self_mute)
                or (not before.channel and after.channel and not (after.mute or after.self_mute))):
            guild_profile.record_voice_activity()

        if ((not before.mute and after.mute)
                or (not before.self_mute and after.self_mute)
                or (before.channel and not after.channel and not (before.mute or before.self_mute))):
            guild_profile.close_voice_activity()

    @Cog.listener()
    async def on_ready(self):
        for g in self.bot.guilds:
            for vc in g.voice_channels:
                for user_id, vs in vc.voice_states.items():
                    user = self.bot.get_user(user_id)
                    if user.bot:
                        continue
                    if vs.self_mute or vs.mute:
                        continue
                    profile = await self.cache.get_profile(user_id)
                    if not profile:
                        profile = await self.cache.create_profile(user_id)
                    guild_profile = await profile.get_guild_profile(g.id)
                    guild_profile.record_voice_activity()
