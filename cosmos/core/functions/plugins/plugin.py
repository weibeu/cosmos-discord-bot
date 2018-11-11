import os

from discord import ClientException
from cosmos.core.functions.data.models import PluginData


class Plugin(object):

    SETUP_FILE = "setup.py"

    def __init__(self, bot, dir_path):
        self.bot = bot
        self.dir_path = dir_path
        self.name = None
        self.raw_path = None    # path to setup.py file.
        self.python_path = None
        # self.category = None
        self.data = None
        self.get_details()
        self.get_data()

    def get_details(self):
        self.name = os.path.basename(self.dir_path)
        self.raw_path = os.path.join(self.dir_path, self.SETUP_FILE)
        self.python_path = f"{self.raw_path.replace('/', '.')}"[:-3]

    def get_data(self):
        self.data = PluginData(self.bot, self)

    def load(self):
        try:
            self.bot.load_extension(self.python_path)
            self.bot.plugins.loaded_plugins.append(self)
            self.bot.log.info(f"Plugin '{self.name}' loaded.")
        except ImportError:
            self.bot.log.info(f"Plugin '{self.name}' failed to load.")
        except ClientException:
            self.bot.log.info(f"Can't find setup function in '{self.name}' plugin.")

    def unload(self):
        self.bot.unload_extension(self.python_path)
        self.bot.plugins.loaded_plugins.remove(self)
        self.bot.log.info(f"Plugin '{self.name}' unloaded.")
