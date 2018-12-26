import os

from .data import Data


class PluginData(Data):

    DATA_DIR = "data/"

    def __init__(self, bot, plugin):
        self.bot = bot
        self.plugin = plugin
        self.data_dir = None    # Raw data.
        self.fetch_plugin_dir()
        super().__init__(self.bot, self.data_dir)   # Vomit plugin data directory to Data superclass.

    def fetch_plugin_dir(self):
        self.data_dir = os.path.join(self.plugin.dir_path, self.DATA_DIR)
