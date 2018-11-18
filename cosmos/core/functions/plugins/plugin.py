import os
import importlib

from discord import ClientException
from cosmos.core.functions.data.models import PluginData


class Plugin(object):

    def __init__(self, bot, dir_path):
        self.bot = bot
        self.dir_path = dir_path
        self.name = None
        self.python_path = None
        # self.category = None
        self.data = None
        self.get_details()
        self.get_data()

    def get_details(self):
        self.name = os.path.basename(self.dir_path)
        self.python_path = f"{self.dir_path.replace('/', '.')}"

    def get_data(self):
        self.data = PluginData(self.bot, self)

    def load(self):
        try:
            if self not in self.bot.plugins.loaded:
                self.bot.load_extension(self.python_path)
                self.bot.plugins.loaded.append(self)
                self.bot.log.info(f"Plugin '{self.name}' loaded.")
            else:
                self.bot.log.info(f"Plugin '{self.name}' is already loaded.")
        except ImportError:
            self.bot.log.info(f"Plugin '{self.name}' failed to load.")
            self.bot.eh.sentry.capture_exception()
        except ClientException as e:
            self.bot.log.info(f"Something went wrong loading '{self.name}' plugin.")
            self.bot.log.info(e)
            self.bot.eh.sentry.capture_exception()

    def unload(self):
        if self in self.bot.plugins.loaded:
            self.bot.unload_extension(self.python_path)
            self.bot.plugins.loaded.remove(self)
            self.bot.log.info(f"Plugin '{self.name}' unloaded.")
        else:
            self.bot.log.info(f"Plugin '{self.name}' isn't loaded.")

    def reload(self):
        if self in self.bot.plugins.loaded:
            importlib.reload(importlib.import_module(self.python_path))
            self.unload()
            self.load()
