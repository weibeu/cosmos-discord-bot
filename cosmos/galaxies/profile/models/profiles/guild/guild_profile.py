class GuildMemberProfile(object):

    def __init__(self, plugin, guild_id, **kwargs):
        self.plugin = plugin
        self.guild_id = guild_id
        self.points = kwargs["points"]
