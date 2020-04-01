class DisabledFunctions(object):

    def __init__(self, bot, document):
        self.__bot = bot
        self.__fetch_commands(document.get("commands", dict()))    # {command_name: [channel_ids], }
        self.__fetch_plugins(document.get("plugins", dict()))
        self.__fetch_galaxies(document.get("galaxies", dict()))

    def __get_channels(self, channel_ids):
        return [self.__bot.get_channel(_) for _ in channel_ids]

    def __fetch_commands(self, _documents):
        for command_name, channel_ids in _documents.items():
            command = self.__bot.get_command(command_name)
            try:
                command.disabled_channels.update(self.__get_channels(channel_ids))
            except AttributeError:
                pass    # Command is inescapable.
            # Dynamically patch channels to which commands are meant to be disabled.
            # command.disabled_channels = [self.__bot.get_channel(_) for _ in channel_ids]
            # Rather than dynamically patching, make commands use custom cls with disabled_channels
            # as one of its attributes and append channels to it.

    def __fetch_plugins(self, _document):
        for plugin_name, channel_ids in _document.items():
            plugin = self.__bot.get_cog(plugin_name)
            try:
                plugin.disabled_channels.update(self.__get_channels(channel_ids))
            except AttributeError:
                pass    # Cog is inescapable.

    def __fetch_galaxies(self, _document):
        for galaxy_name, channel_ids in _document.items():
            galaxy = self.__bot.get_galaxy(galaxy_name.upper())
            try:
                galaxy.disabled_channels.update(self.__get_channels(channel_ids))
            except AttributeError:
                pass    # Galaxy is inescapable.


class GuildPermissions(object):

    def __init__(self, profile, document):
        self.profile = profile
        # self.disabled_commands = []    # function = "commands"
        # self.disabled_plugins = []     # function = "plugins"
        # self.disabled_galaxies = []    # function = "galaxies"
        # Generalisation of above three attributes are represented using '_disabled'.
        disabled_document = document.get("disabled", dict())
        self.disabled = DisabledFunctions(self.profile.plugin.bot, disabled_document.get("functions", dict()))
        # Channels in which bot can't respond to commands or send any kind of message.
        self.disabled_channels = {self.profile.plugin.bot.get_channel(_) for _ in disabled_document.get("channels", [])}

    async def disable_function(self, _, channels):
        _.disabled_channels.update(channels)

        await self.profile.collection.update_one(self.profile.document_filter, {
            "$addToSet": {
                f"settings.permissions.disabled.functions.{_.FUNCTION}.{_.name}": {"$each": [__.id for __ in channels]}
            }
        })

    async def enable_function(self, _, channels):
        _.disabled_channels.difference_update(channels)

        await self.profile.collection.update_one(self.profile.document_filter, {
            "$pull": {
                f"settings.permissions.disabled.functions.{_.FUNCTION}.{_.name}": {"$in": [__.id for __ in channels]}
            }
        })

    async def disable_channels(self, channels):
        self.disabled_channels.update(channels)

        await self.profile.collection.update_one(self.profile.document_filter, {"$addToSet": {
            "settings.permissions.disabled.channels": {"$each": [_.id for _ in channels]}}})

    async def enable_channels(self, channels):
        self.disabled_channels.difference_update(channels)

        await self.profile.collection.update_one(self.profile.document_filter, {"$pull": {
            "settings.permissions.disabled.channels": {"$in": [_.id for _ in channels]}}})
