import os


class Data(object):

    def __init__(self, bot, data):
        self.bot = bot
        self.raw = data    # Universe.
        self.data = []    # List of dicts.
        self.fetch_raw_data()
        self.__setattr()

    def fetch_file(self, file_path):
        self.data.append(self.bot.utilities.file_handler.get_file_data(file_path))

    def fetch_raw_data(self):
        """Converts raw data to data."""
        if isinstance(self.raw, str):   # self.raw maybe path to data directory of file.
            path = self.raw
            if list(os.walk(path)) != list():   # path to directory not file.
                for parent, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(parent, file)
                        self.fetch_file(file_path)
            else:   # path to file or directory doesn't exists.
                if os.path.isfile(self.raw):    # File.
                    self.fetch_file(self.raw)
        elif isinstance(self.raw, dict):    # self.raw is not raw.
            self.data.append(self.raw)
        elif isinstance(self.raw, list):    # self.raw is list containing list of files/path.
            pass
        else:
            try:    # Treat self.raw as file object.
                self.fetch_file(self.raw.name)
            except FileNotFoundError:
                pass
            except IsADirectoryError:
                pass
            else:
                pass    # Mystery.

    def __setattr(self):
        for data in self.data:
            for attr in data:
                self.__setattr__(attr, data[attr])
