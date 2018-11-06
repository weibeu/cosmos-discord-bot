class Data(object):

    def __init__(self, bot, data=None):
        self.bot = bot
        self.raw = data
        self.data = None    # dict
        self.file = None
        self.file_path = None
        self.__setattr()

    def fetch_data(self):
        if isinstance(self.data, str):  # self.raw maybe path to data file.
            self.file_path = self.data
            self.data = self.bot.utilities.file_handler.get_file_data(self.file_path)
        elif isinstance(self.data, dict):
            self.raw = self.data
        else:   # treat self.data as file.
            self.file = self.data
            self.data = self.bot.utilities.file_handler.get_file_data(self.file.name)

    def __setattr(self):
        for attr in self.data:
            self.__setattr__(attr, self.data[attr])
