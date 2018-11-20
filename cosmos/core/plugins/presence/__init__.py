from cosmos.core.plugins.presence.presence import Presence


def setup(bot):
    plugin = bot.plugins.get(bot.utilities.get_file_directory(__file__))
    bot.add_cog(Presence(plugin))
