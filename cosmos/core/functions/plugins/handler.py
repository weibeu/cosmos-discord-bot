import importlib
import os

from discord.utils import get as get_object

from .plugin import Plugin


class PluginHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.fetched = []
        self.loaded = []
        self.fetch_all()

    def fetch_all(self):
        for directory in self.bot.configs.plugins.raw:
            self.bot.log.info(f"Fetching '{directory}' plugins.")
            for plugin_dir in os.listdir(self.bot.configs.plugins.raw[directory]):
                try:
                    plugin_dir_path = os.path.join(self.bot.configs.plugins.raw[directory], plugin_dir)
                    if os.path.isdir(plugin_dir_path):
                        if '__init__.py' in os.listdir(plugin_dir_path):
                            plugin = Plugin(self.bot, plugin_dir_path)
                            self.fetched.append(plugin)
                            self.bot.log.info(f"Fetched '{plugin.name}'. [{plugin.python_path}]")
                        else:
                            pass    # Try loading plugins without '__init__.py'.
                    else:
                        pass    # Not a plugin directory rather maybe a plugin.py file.
                except FileNotFoundError:
                    self.bot.log.info(f"Directory '{self.bot.configs.plugins.raw[directory]}' not found.")
                    self.bot.eh.sentry.capture_exception()

    def get(self, name=None, **kwargs):
        if name:
            return get_object(self.fetched, name=name)
        else:
            return get_object(self.fetched, **kwargs)

    def get_from_file(self, file):
        return self.get(self.bot.utilities.get_file_directory(file))

    def setup(self, file, cogs: list = None, **kwargs):
        plugin = self.get_from_file(file)
        for attr_name in kwargs:
            try:
                attribute = kwargs[attr_name](plugin)
            except TypeError:
                attribute = kwargs[attr_name]
            plugin.__setattr__(attr_name, attribute)
        cog_list = cogs or importlib.import_module(plugin.python_path).__all__
        plugin.load_cogs(cog_list)
        return plugin

    def load_all(self):
        self.bot.log.info("Loading all fetched plugins.")
        for plugin in self.fetched:
            plugin.load()

    def unload_all(self):
        self.bot.log.info("Unloading all loaded plugins.")
        for plugin in self.loaded:
            plugin.unload()

    def refresh(self):
        self.bot.log.info("Refreshing loaded plugins.")
        for plugin in self.loaded:
            plugin.reload()
