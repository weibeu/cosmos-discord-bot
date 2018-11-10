from cosmos.core.functions.data.models import PluginData


class Plugin(object):

    def __init__(self, bot, dir_path):
        self.bot = bot
        self.dir_path = dir_path
        self.name = None
        self.raw_path = None    # path to setup.py file.
        self.python_path = None
        self.category = None
        self.data = None
        self.get_data()

    def get_data(self):
        self.data = PluginData(self.bot, self)

    def load(self):
        pass

    def unload(self):
        pass
