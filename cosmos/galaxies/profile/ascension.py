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

    @staticmethod
    def get_vc_members(voice_channel):
        try:
            return [m for m in voice_channel.members if not m.bot]
        except AttributeError:
            return []

    async def get_guild_profile(self, member_id, guild_id):
        profile = await self.cache.get_profile(member_id)
        return await profile.get_guild_profile(guild_id)

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or after.afk:
            return

        guild_profile = await self.get_guild_profile(member.id, member.guild.id)

        if ((before.mute and not after.mute)
                or (before.self_mute and not after.self_mute)
                or (not before.channel and after.channel and not (after.mute or after.self_mute))):

            # if len(self.get_vc_members(after.channel)) <= 1:
            #     return    # Wait for someone to join vc.

            guild_profile.record_voice_activity()
            guild_profile.profile.record_voice_activity()

        if ((not before.mute and after.mute)
                or (not before.self_mute and after.self_mute)
                or (before.channel and not after.channel and not (before.mute or before.self_mute))):
            guild_profile.close_voice_activity()
            guild_profile.profile.close_voice_activity()

        # if after.channel and not before.channel:
        #     members = self.get_vc_members(before.channel)
        #     if not len(members) == 1:
        #         return
        #     # Someone joined vc. Check and record voice activity for member who is waiting.
        #     waiting_member = members[0]
        #     waiting_member_vs = waiting_member.voice
        #     if waiting_member_vs.self_mute or waiting_member_vs.mute:
        #         return
        #     waiting_profile = await self.get_guild_profile(waiting_member.id, waiting_member.guild.id)
        #     waiting_profile.record_voice_activity()
        #
        # if before.channel and not after.channel:
        #     members = self.get_vc_members(before.channel)
        #     if not len(members) == 1:
        #         return
        #     # Someone left vc and left one member alone. Stop his voice activity.
        #     waiting_member = members[0]
        #     waiting_profile = await self.get_guild_profile(waiting_member.id, waiting_member.guild.id)
        #     waiting_profile.close_voice_activity()

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
                    # if len(self.get_vc_members(vs.channel)):
                    #     continue
                    guild_profile = await self.get_guild_profile(user_id, g.id)
                    guild_profile.record_voice_activity()
                    guild_profile.profile.record_voice_activity()
