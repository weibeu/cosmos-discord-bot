class UserIsBotError(Exception):

    pass


class GuildNotFoundError(Exception):

    def __init__(self, guild_id=None, member_id=None, *args):
        self.guild = guild_id
        self.member = member_id
        super().__init__(*args)
