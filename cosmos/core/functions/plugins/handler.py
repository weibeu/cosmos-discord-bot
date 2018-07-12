import os

from discord import ClientException
from cosmos.core.functions.plugins.plugin import Plugin

class PluginHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.fetched_plugins = []
        self.loaded_plugins = []
        self.fetch_all()

    def fetch_all(self):
        for directory in self.bot.configs.plugins.raw:
            try:
                for plugin_dir in os.listdir(self.bot.configs.plugins.raw[directory]):
                    if os.path.isdir(f"{self.bot.configs.plugins.raw[directory]}/{plugin_dir}"):
                        if 'setup.py' in os.listdir(f"{self.bot.configs.plugins.raw[directory]}/{plugin_dir}"):
                            plugin = Plugin()
                            plugin.name = plugin_dir
                            plugin.raw_path = f"{self.bot.configs.plugins.raw[directory]}/{plugin_dir}/setup.py"
                            plugin.python_path = f"{plugin.raw_path.replace('/', '.')}"[:-3]
                            plugin.category = directory
                            self.fetched_plugins.append(plugin)
            except FileNotFoundError:
                print(f"'{self.bot.configs.plugins.raw[directory]}' directory not found.")

    def load(self, plugin):
        try:
            self.bot.load_extension(plugin.python_path)
            self.loaded_plugins.append(plugin)
            print(f"Plugin {plugin.name} loaded.")
        except ImportError:
            print(f"Plugin {plugin.name} failed to load.")
        except ClientException:
            print(f"Can't find setup function in {plugin.name} plugin.")

    def unload(self, plugin):
        self.bot.unload_extension(plugin.python_path)
        self.loaded_plugins.remove(plugin)
        print(f"Plugin {plugin.name} unloaded.")

    def load_all(self):
        for plugin in self.fetched_plugins:
            self.load(plugin)

    def unload_all(self):
        for plugin in self.loaded_plugins:
            self.unload(plugin)
