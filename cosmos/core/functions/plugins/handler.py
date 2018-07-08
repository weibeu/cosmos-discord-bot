import os

from cosmos.core.functions.plugins.plugin import Plugin

class PluginHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.fetched_plugins = []

    def fetch_all(self):
        for directory in self.bot.configs.plugins.raw:
            for plugin_file_name in os.listdir(self.bot.configs.plugins.raw[directory]):
                if plugin_file_name.endswith(".py"):
                    plugin = Plugin()
                    plugin.name = plugin_file_name[:-3]
                    plugin.raw_path = f"{self.bot.configs.plugins.raw[directory]}/{plugin_file_name}"
                    plugin.python_path = f"{plugin.raw_path.replace('/', '.')}"[:-3]
                    plugin.category = directory
                    self.fetched_plugins.append(plugin)
