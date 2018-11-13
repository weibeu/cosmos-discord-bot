import os

from discord.utils import get as get_object
from cosmos.core.functions.plugins.plugin import Plugin


class PluginHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.fetched = []
        self.loaded = []
        self.fetch_all()

    def fetch_all(self):
        for directory in self.bot.configs.plugins.raw:
            self.bot.log.info(f"Fetching '{directory}' plugins.")
            try:
                for plugin_dir in os.listdir(self.bot.configs.plugins.raw[directory]):
                    plugin_dir_path = os.path.join(self.bot.configs.plugins.raw[directory], plugin_dir)
                    if os.path.isdir(plugin_dir_path):
                        if 'setup.py' in os.listdir(plugin_dir_path):
                            plugin = Plugin(self.bot, plugin_dir_path)
                            self.fetched.append(plugin)
                            self.bot.log.info(f"Fetched '{plugin.name}'. [{plugin.python_path}]")
                        else:
                            pass    # Try loading plugins without 'setup.py'.
                    else:
                        pass    # Not a plugin directory rather maybe a plugin.py file.
            except FileNotFoundError:
                self.bot.log.info(f"Directory '{self.bot.configs.plugins.raw[directory]}' not found.")

    def get(self, **kwargs):
        return get_object(self.fetched, **kwargs)

    @staticmethod
    def load(plugin):
        plugin.load()

    @staticmethod
    def unload(plugin):
        plugin.unload()

    def load_all(self):
        self.bot.log.info("Loading fetched plugins.")
        for plugin in self.fetched:
            self.load(plugin)

    def unload_all(self):
        for plugin in self.loaded:
            self.unload(plugin)
