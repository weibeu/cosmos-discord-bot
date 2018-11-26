import os


class DataEntry(object):

    def __init__(self, data):
        for attr in data:
            self.__setattr__(attr, data[attr])


class Data(object):

    def __init__(self, bot, data):
        self.bot = bot
        self.raw = data    # Universe.
        self.data = {}    # Dict of filename and their corresponding data.
        self.fetch_raw_data()

    def fetch_file(self, file_path):
        base = os.path.basename(file_path)
        self.data[os.path.splitext(base)[0]] = self.bot.utilities.file_handler.get_file_data(file_path)

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
                else:
                    self.data = self.raw
                    return
            self.__setattr()
        elif isinstance(self.raw, dict):    # self.raw is not raw.
            self.data = self.raw
            self.__setattr()
        elif isinstance(self.raw, list):    # self.raw is list containing list of files/path.
            self.data = self.raw
        else:
            try:    # Treat self.raw as file object.
                self.fetch_file(self.raw.name)
            except (FileNotFoundError, IsADirectoryError):
                self.bot.eh.sentry.capture_exception()
            finally:
                self.__setattr()

    def __setattr(self):
        try:
            for name in self.data:
                try:
                    self.__setattr__(name, DataEntry(self.data[name]))
                except TypeError:
                    self.__setattr__(name, self.data[name])
        except TypeError:
            pass
