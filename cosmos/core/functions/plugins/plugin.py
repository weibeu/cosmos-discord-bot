import importlib
import os

from discord import ClientException

from .models import Cog
from ..data.models import PluginData


class Plugin(object):   # Extension    # TODO: Change its name to galaxy.

    FUNCTION = "galaxies"
    INESCAPABLE = True
    # TODO: Auto consume such properties from __init__.py file.

    def __init__(self, bot, dir_path):
        self.bot = bot
        self.dir_path = dir_path
        self.name = None
        self.python_path = None
        self.data = None
        # self.category = None
        # self.extension = None    # __init__.py module.
        self.__disabled_channels = set()    # Set it to False in __init__.py to allow guild admins to disable it.
        self._cogs = {}  # All visible loaded cogs. Isn't affected by load/unload methods.
        self.cogs = {}
        self.get_details()
        self.get_data()

    @property
    def display_name(self):
        return self.name.upper()

    @property
    def disabled_channels(self):
        if self.INESCAPABLE:
            raise AttributeError
        return self.__disabled_channels

    @property
    def module(self):
        return self.bot.extensions.get(self.python_path)

    def get_details(self):
        self.name = os.path.basename(self.dir_path)
        self.python_path = self.dir_path.replace('/', '.').replace('\\', '.')

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

    def load_cog(self, cog):
        cog = cog(self)
        self._cogs.update({cog.name: cog})
        if not isinstance(cog, Cog):
            self.bot.log.warning(f"Can't load COG {cog.name}.")
            self.bot.log.error(f"COG {cog.name} must inherit {Cog.__name__} [{Cog}]")
            return
        if cog.name in self.cogs:
            self.bot.log.error(f"Cog {cog.name} is already loaded.")
            return
        else:
            self.bot.log.info(f"Loading COG {cog.name}.")
            self.bot.add_cog(cog)
            self.cogs.update({cog.name: cog})
        # self._cogs.update({cog.name: cog})
        self.bot.log.info("Done.")

    def load_cogs(self, cogs: list):    # TODO: Fetch all cogs from module.__all__
        for cog in cogs:
            self.load_cog(cog)

    def get_cog(self, cog_name: str):
        return self.cogs.get(cog_name)
