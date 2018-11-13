import json
import yaml


class FileHandler(object):

    def __init__(self, bot):
        self.bot = bot

    def get_file_data(self, path):
        file_data = None
        try:
            file = open(path)
            if path.endswith(".json"):
                file_data = json.load(file)
            elif path.endswith(".yaml") or path.endswith(".yml"):
                file_data = yaml.load(file)
            else:
                self.bot.log.info(f"Unsupported file specified. Ignoring {path}.")
            return file_data    # dict
        except FileNotFoundError:
            self.bot.log.error(f"Unable to find specified file '{path}'.")
            self.bot.eh.sentry.capture_exception()
            return
        except IsADirectoryError:
            self.bot.log.error(f"'{path}' must be path to data file not directory.")
            self.bot.eh.sentry.capture_exception()
            return
