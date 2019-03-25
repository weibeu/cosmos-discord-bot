from ._models import GuildCache


__all__ = [

]


def setup(bot):
    plugin = bot.plugins.get_from_file(__file__)
    plugin.collection = bot.db[plugin.data.guild.collection_name]
    plugin.cache = GuildCache(plugin)

    plugin.load_cogs(__all__)
